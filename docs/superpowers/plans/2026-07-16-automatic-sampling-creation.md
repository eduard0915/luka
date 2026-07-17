# Creación Automática de Muestreos — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear automáticamente los `SamplingProcess` diarios de cada `SamplingGroup` habilitado mediante un management command idempotente con catch-up, disparado por un contenedor cron en Docker Compose (Dokploy).

**Architecture:** Tres piezas desacopladas: (1) servicio de dominio en `core/sampling/services.py` que calcula horarios y crea el lote de un día, (2) management command `generate_samplings` que itera grupos con catch-up e idempotencia respaldada por la tabla `SamplingGenerationLog` (constraint único grupo+fecha), (3) disparador supercronic en compose que corre el comando cada hora. Incluye la corrección del bug de códigos duplicados en `generate_sample_code()`.

**Tech Stack:** Django 5.2.11, PostgreSQL (psycopg2), sin dependencias nuevas de Python. Tests con el runner de Django (`manage.py test`).

**Spec:** `docs/superpowers/specs/2026-07-16-automatic-sampling-creation-design.md`

## Global Constraints

- Sin dependencias nuevas en `requirements.txt`.
- `TIME_ZONE = 'America/Bogota'`, `USE_TZ = True`: todo datetime guardado debe ser aware; los horarios se interpretan en hora local.
- Convenciones del proyecto: modelos heredan de `core.models.BaseModel`, PK `UUIDField(default=uuid.uuid4)`, `db_table` en PascalCase, `verbose_name` en español.
- Muestras automáticas: `type_sampling='En Proceso'`, `automatic_sampling=True`, `status_sampling='Programada'` (default del modelo), `user_creation` nulo.
- Catch-up: máximo 30 días hacia atrás (constante `CATCHUP_MAX_DAYS = 30` en el comando, no un setting).
- Regla "sin punto no hay muestras": grupo deshabilitado, punto deshabilitado (`enable_point=False`) o punto sin `sample_point_code` ⇒ día registrado con `skipped=True` y 0 muestras.
- Los tests corren con `python manage.py test core.sampling -v 2` y requieren el mismo entorno que `runserver` (variables de decouple: `SECRET_KEY`, `DATABASE_TEST`, etc., y PostgreSQL accesible; el runner crea/destruye la base `test_*`).
- Commits pequeños y frecuentes, mensajes en español como el historial existente.

---

### Task 1: Modelo `SamplingGenerationLog`, fixtures de test y migración

**Files:**
- Create: `core/sampling/tests/__init__.py`
- Create: `core/sampling/tests/factories.py`
- Create: `core/sampling/tests/test_models.py`
- Modify: `core/sampling/models.py` (agregar modelo al final del archivo)
- Modify: `core/sampling/admin.py`
- Create: `core/sampling/migrations/0025_samplinggenerationlog.py` (generada por makemigrations; el número puede variar si hay migraciones nuevas)

**Interfaces:**
- Consumes: `SamplingGroup`, `BaseModel` (existentes).
- Produces:
  - Modelo `SamplingGenerationLog(sampling_group: FK[SamplingGroup], target_date: date, samples_created: int = 0, skipped: bool = False)` con constraint único `(sampling_group, target_date)` llamado `unique_group_target_date`.
  - Helpers de test: `build_sample_point(code='PM1', enable_point=True, sample_type='En Proceso', sample_frequency=None) -> SamplePoint` y `build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4, enabled=True, point=None) -> SamplingGroup` en `core.sampling.tests.factories`.

- [ ] **Step 1: Crear el paquete de tests y las fábricas**

`core/sampling/tests/__init__.py`: archivo vacío.

`core/sampling/tests/factories.py`:

```python
import itertools
from datetime import time

from core.company.models import Company, Site
from core.product.models import Product, SamplePoint
from core.sampling.models import SamplingGroup

_sequence = itertools.count(1)


def build_sample_point(code='PM1', enable_point=True, sample_type='En Proceso', sample_frequency=None):
    company = Company.objects.create()
    site = Site.objects.create(
        site_name='Planta Test',
        site_address='Calle 1',
        site_city='Bogotá',
        site_country='Colombia',
        company=company,
    )
    product = Product.objects.create(
        code_product='PROD1',
        description_product='Producto Test',
        site=site,
    )
    return SamplePoint.objects.create(
        sample_point_code=code,
        sample_point_name=f'Punto {code}',
        sequence=next(_sequence),
        product=product,
        sample_type=sample_type,
        sample_frequency=sample_frequency,
        enable_point=enable_point,
    )


def build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4, enabled=True, point=None):
    if point is None:
        point = build_sample_point(code=code)
    return SamplingGroup.objects.create(
        sampling_point=point,
        # time real, no string: la instancia en memoria se usa directo en
        # datetime.combine() dentro de compute_sampling_times
        first_hour_sampling=time.fromisoformat(first_hour),
        number_sampling_day=per_day,
        enable_sampling_group=enabled,
    )
```

- [ ] **Step 2: Escribir el test que falla**

`core/sampling/tests/test_models.py`:

```python
from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog
from core.sampling.tests.factories import build_sampling_group


class SamplingGenerationLogTests(TestCase):
    def test_defaults(self):
        group = build_sampling_group()
        log = SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        self.assertEqual(log.samples_created, 0)
        self.assertFalse(log.skipped)

    def test_unico_por_grupo_y_fecha(self):
        group = build_sampling_group()
        SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
```

- [ ] **Step 3: Verificar que falla**

Run: `python manage.py test core.sampling.tests.test_models -v 2`
Expected: ERROR — `ImportError: cannot import name 'SamplingGenerationLog' from 'core.sampling.models'`

- [ ] **Step 4: Agregar el modelo**

Al final de `core/sampling/models.py`:

```python
# Registro de generación automática de muestras (idempotencia y auditoría)
class SamplingGenerationLog(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_group = models.ForeignKey(SamplingGroup, verbose_name='Grupo de Muestreo', on_delete=models.CASCADE)
    target_date = models.DateField(verbose_name='Día Generado')
    samples_created = models.PositiveSmallIntegerField(verbose_name='Muestras Creadas', default=0)
    skipped = models.BooleanField(verbose_name='Omitido', default=False)

    def __str__(self):
        return f'{self.sampling_group} - {self.target_date}'

    class Meta:
        verbose_name = 'SamplingGenerationLog'
        verbose_name_plural = 'SamplingGenerationLogs'
        db_table = 'SamplingGenerationLog'
        constraints = [
            models.UniqueConstraint(fields=['sampling_group', 'target_date'], name='unique_group_target_date'),
        ]
```

- [ ] **Step 5: Generar y aplicar la migración**

Run: `python manage.py makemigrations sampling`
Expected: `core/sampling/migrations/0025_samplinggenerationlog.py` creada (el número puede variar).

Run: `python manage.py migrate sampling`
Expected: `Applying sampling.0025_samplinggenerationlog... OK`

- [ ] **Step 6: Registrar en el admin**

En `core/sampling/admin.py`, actualizar el import y agregar al final:

```python
from core.sampling.models import SamplingGenerationLog, SamplingGroup, SamplingProcess
```

```python
class SamplingGenerationLogAdmin(admin.ModelAdmin):
    list_display = ('sampling_group', 'target_date', 'samples_created', 'skipped', 'date_creation')
    list_filter = ('skipped', 'target_date')

admin.site.register(SamplingGenerationLog, SamplingGenerationLogAdmin)
```

- [ ] **Step 7: Verificar que pasa**

Run: `python manage.py test core.sampling.tests.test_models -v 2`
Expected: `Ran 2 tests ... OK`

- [ ] **Step 8: Commit**

```bash
git add core/sampling/models.py core/sampling/admin.py core/sampling/migrations/ core/sampling/tests/
git commit -m "Modelo SamplingGenerationLog para generación automática de muestras"
```

---

### Task 2: Códigos de muestra por punto (`next_sample_number`) — corrección del bug

**Files:**
- Modify: `core/sampling/models.py:14-36` (eliminar `code_sample_generator`), `core/sampling/models.py:102-143` (reescribir `generate_sample_code`) — números de línea del archivo ANTES de los cambios; anclar por nombre de función
- Create: `core/sampling/tests/test_sample_codes.py`

**Interfaces:**
- Consumes: `SamplingProcess`, helpers de `core.sampling.tests.factories` (Task 1).
- Produces: función module-level `next_sample_number(sampling_point: SamplePoint, code_date: date) -> str` en `core/sampling/models.py`, formato `{sample_point_code}-{AAAAMMDD}-{n}` con secuencia independiente por punto. `SamplingProcess.generate_sample_code()` delega en ella con `timezone.localdate()`.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_sample_codes.py`:

```python
from datetime import date

from django.test import TestCase
from django.utils import timezone

from core.sampling.models import SamplingProcess, next_sample_number
from core.sampling.tests.factories import build_sample_point


def create_sample(point, number=''):
    return SamplingProcess.objects.create(
        point_sampling=point,
        type_sampling='En Proceso',
        date_sampling_scheduled=timezone.now(),
        number_sample=number,
    )


class NextSampleNumberTests(TestCase):
    def test_secuencia_independiente_por_punto(self):
        # Regresión: intercalar puntos no debe reiniciar ni duplicar la secuencia
        point_a = build_sample_point(code='A')
        point_b = build_sample_point(code='B')
        today_str = timezone.localdate().strftime('%Y%m%d')

        sample_a1 = create_sample(point_a)
        sample_b1 = create_sample(point_b)
        sample_a2 = create_sample(point_a)

        self.assertEqual(sample_a1.number_sample, f'A-{today_str}-1')
        self.assertEqual(sample_b1.number_sample, f'B-{today_str}-1')
        self.assertEqual(sample_a2.number_sample, f'A-{today_str}-2')

    def test_fecha_explicita_para_catchup(self):
        point = build_sample_point(code='PM1')
        self.assertEqual(next_sample_number(point, date(2026, 7, 14)), 'PM1-20260714-1')

    def test_secuencia_continua_con_codigos_existentes(self):
        point = build_sample_point(code='PM1')
        create_sample(point, number='PM1-20260714-1')
        create_sample(point, number='PM1-20260714-2')
        self.assertEqual(next_sample_number(point, date(2026, 7, 14)), 'PM1-20260714-3')

    def test_sin_grupo_ni_punto_lanza_error(self):
        with self.assertRaises(ValueError):
            SamplingProcess.objects.create(
                type_sampling='En Proceso',
                date_sampling_scheduled=timezone.now(),
            )
```

- [ ] **Step 2: Verificar que fallan**

Run: `python manage.py test core.sampling.tests.test_sample_codes -v 2`
Expected: ERROR — `ImportError: cannot import name 'next_sample_number'`

- [ ] **Step 3: Implementar**

En `core/sampling/models.py`:

1. **Eliminar** por completo la función `code_sample_generator` (líneas 14-36, incluido el comentario `# Generador de Número de Muestra`). No tiene usos en el proyecto.

2. **Reemplazar** el método `generate_sample_code` de `SamplingProcess` (líneas 102-143) por:

```python
    def generate_sample_code(self):
        if self.group_sampling:
            sampling_point = self.group_sampling.sampling_point
        elif self.point_sampling:
            sampling_point = self.point_sampling
        else:
            raise ValueError('Debe especificar Grupo de Muestreo o Punto de Muestreo para generar el código de la muestra')
        return next_sample_number(sampling_point, timezone.localdate())
```

3. **Agregar** después de la clase `SamplingProcess` (antes de `SamplingAnalysis`):

```python
# Siguiente código de muestra para un punto en una fecha: {código}-{AAAAMMDD}-{n}.
# La secuencia es independiente por punto de muestreo.
def next_sample_number(sampling_point, code_date):
    prefix = f"{sampling_point.sample_point_code}-{code_date.strftime('%Y%m%d')}-"
    existing = SamplingProcess.objects.filter(
        number_sample__startswith=prefix,
    ).values_list('number_sample', flat=True)
    max_sequence = 0
    for number in existing:
        suffix = number[len(prefix):]
        if suffix.isdigit():
            max_sequence = max(max_sequence, int(suffix))
    return f'{prefix}{max_sequence + 1}'
```

- [ ] **Step 4: Verificar que pasan**

Run: `python manage.py test core.sampling.tests.test_sample_codes -v 2`
Expected: `Ran 4 tests ... OK`

- [ ] **Step 5: Commit**

```bash
git add core/sampling/models.py core/sampling/tests/test_sample_codes.py
git commit -m "Corrige códigos de muestra duplicados: secuencia por punto de muestreo"
```

---

### Task 3: Cálculo de horarios (`compute_sampling_times`)

**Files:**
- Create: `core/sampling/services.py`
- Create: `core/sampling/tests/test_services.py`

**Interfaces:**
- Consumes: `SamplingGroup` (campos `first_hour_sampling`, `number_sampling_day`).
- Produces: `compute_sampling_times(group: SamplingGroup, target_date: date) -> list[datetime]` — datetimes aware en la zona actual (`America/Bogota`), uniformes cada `24h / number_sampling_day` desde `first_hour_sampling`; pueden cruzar a `target_date + 1`.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_services.py`:

```python
from datetime import date, time, timedelta

from django.test import TestCase
from django.utils import timezone

from core.sampling.services import compute_sampling_times
from core.sampling.tests.factories import build_sampling_group

TARGET = date(2026, 7, 16)


class ComputeSamplingTimesTests(TestCase):
    def test_distribucion_uniforme_con_cruce_de_medianoche(self):
        group = build_sampling_group(first_hour='07:00:00', per_day=4)
        times = [timezone.localtime(t) for t in compute_sampling_times(group, TARGET)]
        self.assertEqual(
            [(t.date(), t.time()) for t in times],
            [
                (TARGET, time(7, 0)),
                (TARGET, time(13, 0)),
                (TARGET, time(19, 0)),
                (TARGET + timedelta(days=1), time(1, 0)),
            ],
        )

    def test_intervalo_no_divisor_de_24(self):
        group = build_sampling_group(first_hour='07:00:00', per_day=5)
        times = [timezone.localtime(t).time() for t in compute_sampling_times(group, TARGET)]
        self.assertEqual(times[:2], [time(7, 0), time(11, 48)])

    def test_todos_los_horarios_son_aware(self):
        group = build_sampling_group(per_day=3)
        for t in compute_sampling_times(group, TARGET):
            self.assertFalse(timezone.is_naive(t))
```

- [ ] **Step 2: Verificar que fallan**

Run: `python manage.py test core.sampling.tests.test_services -v 2`
Expected: ERROR — `ModuleNotFoundError: No module named 'core.sampling.services'`

- [ ] **Step 3: Implementar**

`core/sampling/services.py`:

```python
from datetime import datetime, timedelta

from django.utils import timezone


# Horarios del día: intervalo uniforme de 24h / number_sampling_day desde first_hour_sampling.
# Los horarios que cruzan medianoche caen en target_date + 1 pero pertenecen al lote de target_date.
def compute_sampling_times(group, target_date):
    interval = timedelta(hours=24) / group.number_sampling_day
    first = timezone.make_aware(
        datetime.combine(target_date, group.first_hour_sampling),
        timezone.get_current_timezone(),
    )
    return [first + k * interval for k in range(group.number_sampling_day)]
```

Nota: `SamplingGroup.first_hour_sampling` es `TimeField`. La fábrica de tests (Task 1) ya convierte el string a `datetime.time` con `time.fromisoformat`, porque `datetime.combine` requiere un `time` real y la instancia en memoria no pasa por la conversión del ORM.

- [ ] **Step 4: Verificar que pasan**

Run: `python manage.py test core.sampling.tests.test_services -v 2`
Expected: `Ran 3 tests ... OK`

- [ ] **Step 5: Commit**

```bash
git add core/sampling/services.py core/sampling/tests/test_services.py core/sampling/tests/factories.py
git commit -m "Cálculo de horarios de muestreo distribuidos uniformemente en 24h"
```

---

### Task 4: Generación del lote diario (`generate_samplings_for_group`)

**Files:**
- Modify: `core/sampling/services.py`
- Modify: `core/sampling/tests/test_services.py` (agregar clase de tests)

**Interfaces:**
- Consumes: `compute_sampling_times` (Task 3), `next_sample_number` (Task 2), `SamplingGenerationLog` (Task 1).
- Produces:
  - `should_skip_group(group: SamplingGroup) -> bool` — True si el grupo está deshabilitado, el punto está deshabilitado o el punto no tiene código.
  - `generate_samplings_for_group(group: SamplingGroup, target_date: date) -> SamplingGenerationLog | None` — crea el lote en una transacción; devuelve el log creado (con `skipped=True` y 0 muestras si aplica la regla de omisión) o `None` si ese día ya estaba generado.

- [ ] **Step 1: Escribir los tests que fallan**

Agregar al final de `core/sampling/tests/test_services.py`:

```python
from core.sampling.models import SamplingGenerationLog, SamplingProcess
from core.sampling.services import generate_samplings_for_group
from core.sampling.tests.factories import build_sample_point


class GenerateSamplingsForGroupTests(TestCase):
    def test_crea_lote_completo_con_campos_correctos(self):
        group = build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4)
        log = generate_samplings_for_group(group, TARGET)

        self.assertEqual(log.samples_created, 4)
        self.assertFalse(log.skipped)
        samples = SamplingProcess.objects.filter(group_sampling=group).order_by('date_sampling_scheduled')
        self.assertEqual(samples.count(), 4)

        first = samples.first()
        self.assertEqual(first.type_sampling, 'En Proceso')
        self.assertTrue(first.automatic_sampling)
        self.assertEqual(first.status_sampling, 'Programada')
        self.assertIsNone(first.user_creation)
        self.assertEqual(first.number_sample, 'PM1-20260716-1')
        # La muestra que cruza a día siguiente conserva la fecha del lote en su código
        self.assertEqual(samples.last().number_sample, 'PM1-20260716-4')

    def test_idempotente(self):
        group = build_sampling_group(per_day=4)
        self.assertIsNotNone(generate_samplings_for_group(group, TARGET))
        self.assertIsNone(generate_samplings_for_group(group, TARGET))
        self.assertEqual(SamplingProcess.objects.count(), 4)
        self.assertEqual(SamplingGenerationLog.objects.count(), 1)

    def test_grupo_deshabilitado_se_omite(self):
        group = build_sampling_group(enabled=False)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(log.samples_created, 0)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_punto_deshabilitado_se_omite(self):
        point = build_sample_point(code='PM1', enable_point=False)
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_punto_sin_codigo_se_omite(self):
        point = build_sample_point(code='')
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)
```

- [ ] **Step 2: Verificar que fallan**

Run: `python manage.py test core.sampling.tests.test_services -v 2`
Expected: ERROR — `ImportError: cannot import name 'generate_samplings_for_group'`

- [ ] **Step 3: Implementar**

En `core/sampling/services.py`, actualizar imports y agregar:

```python
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingProcess, next_sample_number
```

```python
# Regla "sin punto de muestreo no hay muestras": el grupo debe estar habilitado
# y su punto habilitado y con código.
def should_skip_group(group):
    point = group.sampling_point
    return (
        not group.enable_sampling_group
        or not point.enable_point
        or not point.sample_point_code
    )


# Crea el lote de muestras de un grupo para un día. Devuelve el log creado,
# o None si ese día ya estaba generado (constraint único grupo+fecha).
def generate_samplings_for_group(group, target_date):
    try:
        with transaction.atomic():
            log = SamplingGenerationLog.objects.create(
                sampling_group=group,
                target_date=target_date,
                skipped=should_skip_group(group),
            )
            if log.skipped:
                return log
            point = group.sampling_point
            for scheduled_at in compute_sampling_times(group, target_date):
                SamplingProcess.objects.create(
                    group_sampling=group,
                    type_sampling='En Proceso',
                    date_sampling_scheduled=scheduled_at,
                    automatic_sampling=True,
                    number_sample=next_sample_number(point, target_date),
                )
                log.samples_created += 1
            log.save(update_fields=['samples_created'])
            return log
    except IntegrityError:
        return None
```

- [ ] **Step 4: Verificar que pasan**

Run: `python manage.py test core.sampling.tests.test_services -v 2`
Expected: `Ran 8 tests ... OK`

- [ ] **Step 5: Verificar que no se rompió nada**

Run: `python manage.py test core.sampling -v 2`
Expected: todos los tests OK.

- [ ] **Step 6: Commit**

```bash
git add core/sampling/services.py core/sampling/tests/test_services.py
git commit -m "Servicio de generación de lote diario de muestras por grupo"
```

---

### Task 5: Management command `generate_samplings`

**Files:**
- Create: `core/sampling/management/__init__.py`
- Create: `core/sampling/management/commands/__init__.py`
- Create: `core/sampling/management/commands/generate_samplings.py`
- Create: `core/sampling/tests/test_command.py`

**Interfaces:**
- Consumes: `generate_samplings_for_group`, `should_skip_group`, `compute_sampling_times` (Tasks 3-4), `SamplingGenerationLog` (Task 1).
- Produces: comando `python manage.py generate_samplings [--date YYYY-MM-DD] [--dry-run]`. Resumen en stdout `'{N} muestras creadas, {M} días generados, {E} grupos con error'`; lanza `CommandError` (exit code 1) si hubo errores.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_command.py`:

```python
from datetime import date
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog, SamplingProcess
from core.sampling.tests.factories import build_sampling_group


def run(*args, **kwargs):
    out = StringIO()
    call_command('generate_samplings', *args, stdout=out, stderr=out, **kwargs)
    return out.getvalue()


class GenerateSamplingsCommandTests(TestCase):
    def test_crea_las_muestras_del_dia(self):
        build_sampling_group(per_day=3)
        output = run(date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 3)
        self.assertIn('3 muestras creadas', output)

    def test_idempotente_correr_dos_veces(self):
        build_sampling_group(per_day=3)
        run(date='2026-07-16')
        run(date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 3)
        self.assertEqual(SamplingGenerationLog.objects.count(), 1)

    def test_catchup_de_dias_perdidos(self):
        group = build_sampling_group(per_day=2)
        run(date='2026-07-10')
        run(date='2026-07-13')  # 3 días sin correr
        dates = list(
            SamplingGenerationLog.objects.filter(sampling_group=group)
            .order_by('target_date')
            .values_list('target_date', flat=True)
        )
        self.assertEqual(dates, [date(2026, 7, 10), date(2026, 7, 11), date(2026, 7, 12), date(2026, 7, 13)])
        self.assertEqual(SamplingProcess.objects.count(), 8)

    def test_catchup_respeta_tope_de_30_dias(self):
        group = build_sampling_group(per_day=1)
        run(date='2026-01-01')
        run(date='2026-07-16')  # mucho más de 30 días después
        posteriores = SamplingGenerationLog.objects.filter(
            sampling_group=group, target_date__gt=date(2026, 1, 1)
        )
        self.assertEqual(posteriores.earliest('target_date').target_date, date(2026, 6, 16))
        self.assertEqual(posteriores.count(), 31)  # 2026-06-16 a 2026-07-16 inclusive

    def test_grupo_deshabilitado_sin_backfill_al_rehabilitar(self):
        group = build_sampling_group(per_day=2, enabled=False)
        run(date='2026-07-15')
        self.assertEqual(SamplingProcess.objects.count(), 0)
        self.assertTrue(
            SamplingGenerationLog.objects.get(sampling_group=group, target_date=date(2026, 7, 15)).skipped
        )

        group.enable_sampling_group = True
        group.save()
        run(date='2026-07-16')
        # Solo se genera el día actual; el período deshabilitado no se rellena
        self.assertEqual(SamplingProcess.objects.count(), 2)
        self.assertEqual(
            SamplingGenerationLog.objects.filter(sampling_group=group, skipped=False).count(), 1
        )

    def test_dry_run_no_escribe(self):
        build_sampling_group(per_day=3)
        output = run('--dry-run', date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 0)
        self.assertEqual(SamplingGenerationLog.objects.count(), 0)
        self.assertIn('dry-run', output)

    def test_error_en_un_grupo_no_bloquea_los_demas(self):
        build_sampling_group(code='MAL', per_day=0)  # 24h / 0 → ZeroDivisionError
        build_sampling_group(code='OK', per_day=2)
        with self.assertRaises(CommandError):
            run(date='2026-07-16')
        creados = SamplingProcess.objects.filter(
            group_sampling__sampling_point__sample_point_code='OK'
        )
        self.assertEqual(creados.count(), 2)
```

- [ ] **Step 2: Verificar que fallan**

Run: `python manage.py test core.sampling.tests.test_command -v 2`
Expected: ERROR — `Unknown command: 'generate_samplings'` (o `CommandError` equivalente en cada test).

- [ ] **Step 3: Implementar el comando**

`core/sampling/management/__init__.py` y `core/sampling/management/commands/__init__.py`: archivos vacíos.

`core/sampling/management/commands/generate_samplings.py`:

```python
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingGroup
from core.sampling.services import (
    compute_sampling_times,
    generate_samplings_for_group,
    should_skip_group,
)

CATCHUP_MAX_DAYS = 30


class Command(BaseCommand):
    help = 'Crea las muestras programadas (SamplingProcess) del día para cada grupo de muestreo, con recuperación de días perdidos'

    def add_arguments(self, parser):
        parser.add_argument('--date', help="Simula la fecha de 'hoy' (YYYY-MM-DD); para pruebas y operación manual")
        parser.add_argument('--dry-run', action='store_true', help='Reporta lo que se crearía sin escribir en la base de datos')

    def handle(self, *args, **options):
        if options['date']:
            today = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            today = timezone.localdate()
        dry_run = options['dry_run']

        total_created = 0
        days_generated = 0
        errors = 0

        for group in SamplingGroup.objects.select_related('sampling_point').order_by('date_creation'):
            try:
                created, days = self._process_group(group, today, dry_run)
                total_created += created
                days_generated += days
            except Exception as exc:
                errors += 1
                self.stderr.write(f'ERROR en grupo {group.id} ({group}): {exc}')

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(
            f'{prefix}{total_created} muestras creadas, {days_generated} días generados, {errors} grupos con error'
        )
        if errors:
            raise CommandError(f'{errors} grupos con error')

    def _process_group(self, group, today, dry_run):
        last = SamplingGenerationLog.objects.filter(sampling_group=group).aggregate(
            last=Max('target_date')
        )['last']
        start = last + timedelta(days=1) if last else today
        floor = today - timedelta(days=CATCHUP_MAX_DAYS)
        if start < floor:
            start = floor

        created = 0
        days = 0
        day = start
        while day <= today:
            if dry_run:
                if should_skip_group(group):
                    self.stdout.write(f'[dry-run] {group}: omitido para {day}')
                else:
                    times = compute_sampling_times(group, day)
                    self.stdout.write(f'[dry-run] {group}: {len(times)} muestras para {day}')
                    days += 1
                    created += len(times)
            else:
                log = generate_samplings_for_group(group, day)
                if log is not None and not log.skipped:
                    days += 1
                    created += log.samples_created
            day += timedelta(days=1)
        return created, days
```

- [ ] **Step 4: Verificar que pasan**

Run: `python manage.py test core.sampling.tests.test_command -v 2`
Expected: `Ran 7 tests ... OK`

- [ ] **Step 5: Prueba de humo manual**

Run: `python manage.py generate_samplings --dry-run`
Expected: líneas `[dry-run] ...` por cada grupo con días pendientes (o solo el resumen si no hay grupos) y exit code 0.

- [ ] **Step 6: Commit**

```bash
git add core/sampling/management/ core/sampling/tests/test_command.py
git commit -m "Comando generate_samplings con catch-up e idempotencia"
```

---

### Task 6: Validación del formulario manual (grupo o punto requerido)

**Files:**
- Modify: `core/sampling/forms.py:360-368` (método `clean` de `SamplingProcessForm`)
- Create: `core/sampling/tests/test_forms.py`

**Interfaces:**
- Consumes: `SamplingProcessForm` existente (`ValidationError` ya está importado en `forms.py`).
- Produces: `SamplingProcessForm` inválido con error no-de-campo `'Debe seleccionar un Grupo de Muestreo o un Punto de Muestreo.'` cuando ambos campos vienen vacíos.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_forms.py`:

```python
from django.test import TestCase

from core.sampling.forms import SamplingProcessForm
from core.sampling.tests.factories import build_sampling_group


class SamplingProcessFormTests(TestCase):
    def test_sin_grupo_ni_punto_es_invalido(self):
        form = SamplingProcessForm(data={
            'type_sampling': 'En Proceso',
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Debe seleccionar un Grupo de Muestreo o un Punto de Muestreo.',
            form.non_field_errors(),
        )

    def test_con_grupo_es_valido(self):
        group = build_sampling_group()
        form = SamplingProcessForm(data={
            'type_sampling': 'En Proceso',
            'group_sampling': group.pk,
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertTrue(form.is_valid(), form.errors)
```

- [ ] **Step 2: Verificar que falla**

Run: `python manage.py test core.sampling.tests.test_forms -v 2`
Expected: FAIL — `test_sin_grupo_ni_punto_es_invalido` falla porque el formulario es válido sin grupo ni punto (el segundo test debe pasar desde ya).

- [ ] **Step 3: Implementar**

En `core/sampling/forms.py`, dentro de `SamplingProcessForm.clean()` (línea ~360), agregar la validación antes de los `if` existentes:

```python
    def clean(self):
        cleaned_data = super().clean()
        group_sampling = cleaned_data.get('group_sampling')
        point_sampling = cleaned_data.get('point_sampling')
        if not group_sampling and not point_sampling:
            raise ValidationError('Debe seleccionar un Grupo de Muestreo o un Punto de Muestreo.')
        if group_sampling:
            cleaned_data['point_sampling'] = None
        if point_sampling:
            cleaned_data['group_sampling'] = None
        return cleaned_data
```

- [ ] **Step 4: Verificar que pasan**

Run: `python manage.py test core.sampling.tests.test_forms -v 2`
Expected: `Ran 2 tests ... OK`

- [ ] **Step 5: Correr la suite completa de sampling**

Run: `python manage.py test core.sampling -v 2`
Expected: todos los tests OK (los 4 archivos de test).

- [ ] **Step 6: Commit**

```bash
git add core/sampling/forms.py core/sampling/tests/test_forms.py
git commit -m "Valida que toda muestra manual tenga grupo o punto de muestreo"
```

---

### Task 7: Infraestructura — crontab y documentación de despliegue

**Files:**
- Create: `crontab`
- Create: `docs/deploy/scheduler.md`

**Interfaces:**
- Consumes: comando `generate_samplings` (Task 5).
- Produces: archivo `crontab` para supercronic y guía de integración con el compose de Dokploy.

- [ ] **Step 1: Crear el archivo crontab**

`crontab` (raíz del repo):

```
# Generación automática de muestreos: cada hora al minuto 10.
# La primera corrida del día crea el lote completo; las demás son no-ops (idempotente).
10 * * * * python manage.py generate_samplings
```

- [ ] **Step 2: Documentar la integración**

`docs/deploy/scheduler.md`:

````markdown
# Scheduler de muestreos automáticos (Dokploy / Docker Compose)

El comando `python manage.py generate_samplings` crea las muestras programadas
del día para cada grupo de muestreo habilitado. Es idempotente y recupera hasta
30 días perdidos, por lo que puede ejecutarse las veces que sea sin duplicar.

## Opción A — Servicio supercronic en el compose (recomendada, portable)

Agregar al `docker-compose.yml` del despliegue un servicio con la misma imagen
de la app. La imagen debe incluir el binario de supercronic
(https://github.com/aptible/supercronic), por ejemplo en el Dockerfile:

```dockerfile
ADD https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic
```

```yaml
scheduler:
  image: <misma imagen de la app>
  command: supercronic /app/crontab
  working_dir: /app
  environment:
    TZ: America/Bogota
  env_file:
    - .env   # mismas variables que la app (DATABASE_URL, SECRET_KEY, ...)
  depends_on:
    - db
  restart: unless-stopped
```

El archivo `crontab` de la raíz del repo ejecuta el comando cada hora al
minuto 10. La frecuencia horaria cubre el caso "servidor caído a medianoche,
recuperado durante el día".

## Opción B — Scheduled Tasks de Dokploy (sin contenedor extra)

En Dokploy, crear una Scheduled Task sobre el servicio de la app:

- Comando: `python manage.py generate_samplings`
- Programación: `10 * * * *`

## Monitoreo

- El comando termina con exit code 1 si algún grupo falló (los demás se
  procesan igual); los detalles quedan en stderr (logs del contenedor).
- Cada día generado queda auditado en la tabla `SamplingGenerationLog`
  (visible en el admin de Django), incluidos los días omitidos por grupo o
  punto deshabilitado (`skipped=True`).
- Verificación manual sin escribir: `python manage.py generate_samplings --dry-run`.
````

- [ ] **Step 3: Verificación final de la suite**

Run: `python manage.py test core.sampling -v 2`
Expected: todos los tests OK.

- [ ] **Step 4: Commit**

```bash
git add crontab docs/deploy/scheduler.md
git commit -m "Crontab y guía de despliegue del scheduler de muestreos"
```
