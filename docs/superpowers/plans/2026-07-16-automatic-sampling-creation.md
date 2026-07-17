# Creación Automática de Muestreos — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear automáticamente los `SamplingProcess` diarios de cada `SamplingGroup` habilitado mediante un management command idempotente con catch-up, disparado por un contenedor cron en Docker Compose (Dokploy).

**Architecture:** Tres piezas desacopladas: (1) servicio de dominio en `core/sampling/services.py` que calcula horarios y crea el lote de un día, (2) management command `generate_samplings` que itera grupos con catch-up e idempotencia respaldada por la tabla `SamplingGenerationLog` (constraint único grupo+fecha), (3) disparador supercronic en compose que corre el comando cada hora. Incluye la corrección del bug de códigos duplicados en `generate_sample_code()`.

**Tech Stack:** Django 6.0.7, PostgreSQL 16 (psycopg2-binary 2.9.11) vía dj-database-url 3.1.2, Python 3.12 (`Dockerfile`: `FROM python:3.12-slim-bookworm`), sin dependencias nuevas de Python. Tests con el runner de Django (`manage.py test`, ejecutado en Docker — ver Global Constraints).

**Spec:** `docs/superpowers/specs/2026-07-16-automatic-sampling-creation-design.md`

> **Estado: EJECUTADO.** Este plan ya se implementó por completo (32 tests en verde).
> Se conserva como registro del diseño de la construcción. Dos diferencias entre lo
> planeado y lo entregado, ambas deliberadas:
> - `makemigrations` emitió una sola migración, `0032_samplinggenerationlog_y_endurecimiento.py`,
>   en vez de las dos que el plan separa (0032 para el modelo de log y 0033 para el
>   endurecimiento de campos). Un solo archivo es más simple y aplica de forma atómica.
> - Los conteos de tests por task son los del plan; la suite final tiene 32 tests.

## Global Constraints

- Sin dependencias nuevas en `requirements.txt`.
- `TIME_ZONE = 'America/Bogota'`, `USE_TZ = True`: todo datetime guardado debe ser aware; los horarios se interpretan en hora local.
- Convenciones del proyecto: modelos heredan de `core.models.BaseModel`, PK `UUIDField(default=uuid.uuid4)`, `db_table` en PascalCase, `verbose_name` en español.
- Muestras automáticas: `type_sampling='En Proceso'`, `automatic_sampling=True`, `status_sampling='Programada'` (default del modelo), `user_creation` nulo.
- Catch-up: máximo 30 días hacia atrás (constante `CATCHUP_MAX_DAYS = 30` en el comando, no un setting).
- Regla "sin punto no hay muestras": grupo deshabilitado, punto deshabilitado (`enable_point=False`) o punto sin `sample_point_code` ⇒ día registrado con `skipped=True` y 0 muestras.
- Alcance de periodicidad: esta feature SOLO genera muestras para puntos diarios. Los puntos `'Semanal'` y `'Mensual'` se registran con `skipped=True` y 0 muestras. `'Diario'` (masculino, default histórico del modelo) y `'Diaria'` (choice de la UI) cuentan AMBOS como diario; NO se normalizan datos existentes ni se cambia el default del modelo.
- No hay intérprete de Python usable en el host (`.venv` solo trae pip; `python` no está en PATH y el `python3` del sistema no tiene Django instalado): TODO comando de Django de este plan se ejecuta en Docker montando el working tree. Comando canónico:
  ```bash
  docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling -v 2
  ```
  El bind mount `-v "$PWD:/app"` es OBLIGATORIO, no opcional: el `Dockerfile` hace `COPY . .` y `web-luka` solo monta `static_volume:/app/static` y `media_volume:/app/media`, así que sin él el contenedor ejecutaría el código horneado en la imagen (los tests nuevos no existirían dentro) y peor aún, el archivo que genere `makemigrations` se escribiría dentro del contenedor y `--rm` lo destruiría. Sustituir de la misma forma TODOS los `python manage.py ...` de las Tasks 1-7 (`test`, `makemigrations`, `migrate` y `generate_samplings --dry-run`). Tras cada `makemigrations`, verificar en el host que el archivo apareció con `ls core/sampling/migrations/` antes de commitear.
- Variables de entorno: `DATABASE_TEST` ya NO existe (estaba en `main`, eliminada en `dev`). `luka/settings.py:91-97` define la base únicamente con `dj_database_url.config(default=config('DATABASE_URL'), conn_max_age=600, conn_health_checks=True)` y sin clave `TEST`, por lo que el runner crea/destruye `test_<nombre>` derivada de esa MISMA `DATABASE_URL` que usa la app — atención si apunta a un entorno compartido. Requiere un `.env` en la raíz del repo (no versionado; hoy no existe) con al menos:
  ```
  POSTGRES_DB=luka
  POSTGRES_USER=luka
  POSTGRES_PASSWORD=luka
  DATABASE_URL=postgres://luka:luka@db-luka:5432/luka
  SECRET_KEY=dev-secret-para-tests
  DEBUG=True
  MEDIA_URL=/media/
  ```
  `docker compose run` levanta `db-luka` y espera su healthcheck (`depends_on: condition: service_healthy`). Las variables `AWS_*`/`BUCKET`/`REGION_NAME`/`EMAIL_*` pueden quedar sin declarar: la forma `- VAR=${VAR}` del compose las inyecta como cadena vacía y compose solo emite warnings `variable is not set`, inocuos.
- Trampa de configuración al depurar: el proyecto pinnea `django-decouple==2.1` (fork antiguo, NO `python-decouple`). Su `config()` está declarado `def get(self, option, default=string_empty, cast=string_type)` y devuelve `''` en silencio cuando la variable falta — `UndefinedValueError` NO existe en ese paquete. Por eso ninguna de las 7 llamadas `config()` sin default de `settings.py` (`SECRET_KEY`:17, `DEBUG`:19, `DATABASE_URL`:93, `AWS_ACCESS_KEY_ID`:181, `AWS_SECRET_ACCESS_KEY`:182, `BUCKET`:183, `REGION_NAME`:184) aborta el arranque por ausencia. Consecuencia: si falta `DATABASE_URL`, `dj_database_url.config(default='')` devuelve `{}` y el error llega tarde y confuso como `ImproperlyConfigured: settings.DATABASES is improperly configured. Please supply the ENGINE value.`; si `SECRET_KEY` queda vacía, Django 6.0.7 lanza `ImproperlyConfigured: The SECRET_KEY setting must not be empty.`.
- Todos los números de línea de este plan y del spec son relativos al estado del archivo ANTES de los cambios y se derivaron originalmente de `main`: pueden estar desfasados. Resolver SIEMPRE toda referencia numérica por nombre de símbolo (función, método o clase) antes de editar.
- Commits pequeños y frecuentes, mensajes en español como el historial existente.

---

### Task 1: Modelo `SamplingGenerationLog`, fixtures de test y migración

**Files:**
- Create: `core/sampling/tests/__init__.py`
- Create: `core/sampling/tests/factories.py`
- Create: `core/sampling/tests/test_models.py`
- Modify: `core/sampling/models.py` (agregar modelo al final del archivo)
- Modify: `core/sampling/admin.py`
- Create: `core/sampling/migrations/0032_samplinggenerationlog.py` (generada por makemigrations; el número lo asigna makemigrations a partir de la última migración del app, hoy 0031)

**Interfaces:**
- Consumes: `SamplingGroup`, `BaseModel` (existentes).
- Produces:
  - Modelo `SamplingGenerationLog(sampling_group: FK[SamplingGroup], target_date: date, samples_created: int = 0, skipped: bool = False)` con constraint único `(sampling_group, target_date)` llamado `unique_group_target_date`.
  - Helpers de test: `build_sample_point(code='PM1', enable_point=True, sample_type='En Proceso', sample_frequency=None, periodicity='Diaria') -> SamplePoint` y `build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4, enabled=True, point=None) -> SamplingGroup` en `core.sampling.tests.factories`.

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


def build_sample_point(code='PM1', enable_point=True, sample_type='En Proceso', sample_frequency=None, periodicity='Diaria'):
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
        periodicity=periodicity,
        enable_point=enable_point,
    )


def build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4, enabled=True, point=None):
    if point is None:
        # Coherente con la UI: N = floor(24 / sample_frequency)
        point = build_sample_point(code=code, sample_frequency=24 // per_day if per_day else None)
    return SamplingGroup.objects.create(
        sampling_point=point,
        # time real, no string: la instancia en memoria se usa directo en
        # datetime.combine() dentro de compute_sampling_times
        first_hour_sampling=time.fromisoformat(first_hour),
        number_sampling_day=per_day,
        enable_sampling_group=enabled,
    )
```

Dos decisiones deliberadas en las fábricas:

- `periodicity='Diaria'` es explícito y NO se deja al default del modelo (`core/product/models.py:102` trae `default='Diario'`, el valor legacy masculino): los tests no deben depender de ese default.
- `sample_frequency` se deriva de `per_day` porque `SamplingGroupForm` (`core/sampling/forms.py:331`) solo admite puntos con `sample_frequency` no nulo; sin esto las fábricas producirían grupos improducibles por la UI. El guard `if per_day else None` preserva el caso `per_day=0` que usan los tests de omisión.

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

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_models -v 2`
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

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py makemigrations sampling`
Expected: `core/sampling/migrations/0032_samplinggenerationlog.py` creada (el número lo asigna makemigrations desde la última migración del app, hoy 0031).

Run: `ls core/sampling/migrations/`
Expected: el archivo aparece en el host (confirma que el bind mount funcionó y que `--rm` no se lo llevó).

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py migrate sampling`
Expected: `Applying sampling.0032_samplinggenerationlog... OK` (el número depende de la última migración aplicada, hoy 0031; si entran migraciones nuevas antes, será el siguiente consecutivo).

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

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_models -v 2`
Expected: `Ran 2 tests ... OK`

- [ ] **Step 8: Commit**

```bash
git add core/sampling/models.py core/sampling/admin.py core/sampling/migrations/ core/sampling/tests/
git commit -m "Modelo SamplingGenerationLog para generación automática de muestras"
```

---

### Task 2: Códigos de muestra por punto (`next_sample_number`) — corrección del bug

**Files:**
- Modify: `core/sampling/models.py:15-37` (eliminar `code_sample_generator`), `core/sampling/models.py:112-153` (reescribir `generate_sample_code`), `core/sampling/models.py:74` y `:45` (endurecer campos), `core/sampling/models.py:99-110` (envolver `save` en `atomic`) — números ANTES de los cambios; anclar por nombre de función
- Modify: `core/sampling/migrations/0001_initial.py` (quitar la referencia a `code_sample_generator`)
- Modify: `core/sampling/migrations/0005_alter_samplingprocess_number_sample.py` (quitar la referencia a `code_sample_generator`)
- Create: `core/sampling/migrations/0033_hardening_codigos_y_muestras_por_dia.py` (generada por makemigrations; 0032 la ocupa el modelo de Task 1)
- Create: `core/sampling/tests/test_sample_codes.py`

**Interfaces:**
- Consumes: `SamplingProcess`, `SamplePoint`, helpers de `core.sampling.tests.factories` (Task 1).
- Produces: función module-level `next_sample_number(sampling_point: SamplePoint, code_date: date) -> str` en `core/sampling/models.py`, formato `{sample_point_code}-{AAAAMMDD}-{n}` con secuencia independiente por punto, serializada con `select_for_update()` sobre el punto. `SamplingProcess.generate_sample_code()` delega en ella con `timezone.localdate()`, y `SamplingProcess.save()` envuelve generación e INSERT en un único `transaction.atomic()`.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_sample_codes.py`:

```python
from datetime import date

from django.test import TestCase
from django.utils import timezone

from core.product.models import SamplePoint
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

    def test_codigo_largo_no_desborda_number_sample(self):
        # Regresión: sample_point_code admite 30 chars y el código completo debe caber.
        code = 'PUNTO-MUESTREO-LARGO-123456789'  # 30 chars = máximo de sample_point_code
        point = build_sample_point(code=code)
        sample = create_sample(point)
        today_str = timezone.localdate().strftime('%Y%m%d')
        self.assertEqual(sample.number_sample, f'{code}-{today_str}-1')

    def test_number_sample_cubre_el_maximo_de_sample_point_code(self):
        # Ata el acoplamiento entre los dos campos: {code}-{AAAAMMDD}-{n} => code_max + 1 + 8 + 1 + 5
        code_max = SamplePoint._meta.get_field('sample_point_code').max_length
        number_max = SamplingProcess._meta.get_field('number_sample').max_length
        self.assertGreaterEqual(number_max, code_max + 15)
```

Los dos últimos tests son el blindaje del bug que pasaría desapercibido: las fábricas usan códigos de 1-3 chars (`'PM1'` → 14 chars justos, caben en `varchar(25)`), así que todo saldría verde en tests y reventaría en producción. `test_codigo_largo_no_desborda_number_sample` falla con `DataError` antes de la migración del Step 3 y pasa después. `test_number_sample_cubre_el_maximo_de_sample_point_code` es el que más importa: sin él el 45 queda como comentario y el acoplamiento se rompe de nuevo si alguien amplía `sample_point_code` — precedente exacto: `number_sample` ya pasó de 15 a 25 en la migración 0005 por esta misma razón.

- [ ] **Step 2: Verificar que fallan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_sample_codes -v 2`
Expected: ERROR — `ImportError: cannot import name 'next_sample_number'`

- [ ] **Step 3a: Despojar a las migraciones históricas de la referencia**

Dos migraciones históricas referencian `code_sample_generator` a nivel de módulo (`core/sampling/migrations/0001_initial.py:3` y `:47`; `core/sampling/migrations/0005_alter_samplingprocess_number_sample.py:3` y `:17`). El `MigrationLoader` de Django importa TODAS las migraciones de la app en cualquier comando que toque el grafo, así que borrar la función sin este paso produce `AttributeError: module 'core.sampling.models' has no attribute 'code_sample_generator'` y revienta `migrate`, `makemigrations`, el `CMD python manage.py migrate` del Dockerfile y `manage.py test` (que construye la BD de test corriendo las 31 migraciones). Este step va ANTES del Step 3.

- En `core/sampling/migrations/0001_initial.py`, borrar la línea 3 (`import core.sampling.models`) y cambiar la línea 47 a:
  ```python
                  ('number_sample', models.CharField(max_length=15, verbose_name='N° de Muestras')),
  ```
- En `core/sampling/migrations/0005_alter_samplingprocess_number_sample.py`, borrar la línea 3 (`import core.sampling.models`) y cambiar la línea 17 a:
  ```python
              field=models.CharField(max_length=25, verbose_name='N° de Muestra'),
  ```
- En ambos archivos `import core.sampling.models` no se usa en ninguna otra línea, así que puede borrarse sin más.

Por qué es seguro (verificado, no asumido): la migración `0006` ya hace un `AlterField` a `models.CharField(max_length=25, verbose_name='N° de Muestra')` sin default, y el modelo tampoco declara default, de modo que el estado final del grafo NO cambia y `makemigrations --check` no detecta deriva (0005 queda idéntica a 0006: un AlterField redundante pero idempotente e inocuo). `default` en Django es de aplicación, no de esquema (no es `db_default`): 0001 es un `CreateModel` sin filas y 0005 un `AlterField` de `max_length`, así que hay cero efecto en la BD. Editar migraciones ya aplicadas es seguro porque `django_migrations` registra solo `(app, name)`, sin checksum, y no existe ninguna `RunPython`/`RunSQL` en el repo que use el modelo histórico.

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py makemigrations --check --dry-run sampling`
Expected: no reporta ningún cambio sobre `number_sample`.

Esta verificación es NECESARIA pero INSUFICIENTE por sí sola. Acompañarla del comando que realmente reproduce el `AttributeError` (import del grafo completo sobre una BD creada desde cero):

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py migrate sampling`
Expected: `No migrations to apply.` (o las pendientes aplicadas OK) — sin `AttributeError`.

- [ ] **Step 3: Implementar**

En `core/sampling/models.py`:

**0. Endurecer los campos del modelo.** En la línea 74:

```python
    number_sample = models.CharField(verbose_name='N° de Muestra', max_length=45)
```

Cota: `30 (sample_point_code) + 1 + 8 (AAAAMMDD) + 1 + 5 (n; number_sampling_day es PositiveSmallIntegerField, máx. 32767) = 45`. Esto es exactamente lo que faltó en la migración 0005, donde se pasó de 15 a 25 a ojo. `number_sample` es hoy `max_length=25` pero `sample_point_code` admite 30 (`core/product/models.py:95`), y el código generado mide `len(code) + 1 + 8 + 1 + len(str(n))` — hasta 41-42 caracteres: cualquier código de punto de más de 13-14 caracteres produce `django.db.utils.DataError: value too long for type character varying(25)`, que NO es subclase de `IntegrityError` (son hermanos bajo `django.db.Error`), escapa del `except IntegrityError` de `generate_samplings_for_group`, revierte el día completo, el log nunca se escribe y el comando sale con exit code 1 en CADA corrida horaria.

Y en la línea 45:

```python
    number_sampling_day = models.PositiveSmallIntegerField(verbose_name='Muestras por Día', validators=[MinValueValidator(1)])
```

con el import `from django.core.validators import MinValueValidator` (defensa en profundidad para el admin —`core/sampling/admin.py` registra un ModelAdmin plano que corre `full_clean`— y para POST manipulados; la guarda de ejecución vive en `should_skip_group`, Task 4). NO cambiar el widget a `NumberInput(min=1)`: el campo es `readonly` y lo puebla JS (`core/sampling/static/form_sampling_group.js:11,29-30`), el atributo `min` nunca se dispara.

La migración es INCONDICIONAL: no gatearla tras un `SELECT max(length(sample_point_code))` sobre producción. El implementador no tiene acceso a esa BD (`DATABASE_URL` es un secreto inyectado por Dokploy) y el dato del día es irrelevante — el campo **permite 30** y la UI lo expone como `TextInput` sin validadores, así que aunque hoy el máximo fuera 8, mañana alguien crea `TANQUE-PRINCIPAL-01`. La cota se deriva del límite DECLARADO del campo.

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py makemigrations sampling -n hardening_codigos_y_muestras_por_dia`
Expected: `core/sampling/migrations/0033_hardening_codigos_y_muestras_por_dia.py` (0032 la ocupa el modelo de Task 1; las migraciones preexistentes llegan a 0031).

Es una migración barata y segura en producción: PostgreSQL **no reescribe la tabla** al ampliar el límite de un `varchar` (optimización de metadatos desde 9.2), así que no hay ventana de bloqueo aunque `SamplingProcess` tenga volumen; y los validators no tocan el esquema.

**1. Eliminar** por completo la función `code_sample_generator` (líneas 15-37, incluido el comentario `# Generador de Número de Muestra` de la línea 15). No tiene usos en código de producción; las únicas referencias eran las migraciones históricas 0001 y 0005, despojadas en el Step 3a anterior.

**2. Reemplazar** el método `generate_sample_code` de `SamplingProcess` (líneas 112-153) por:

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

El bloque a reemplazar termina en el `return f'{sufix_sample}-{today_str}-1'` del `else` final (línea 153), NO en el `return` del `if last_sample` (línea 150): ambos returns son idénticos y confunden al anclar visualmente.

**3. Agregar** después de la clase `SamplingProcess` (antes de `SamplingAnalysis`):

```python
# Siguiente código de muestra para un punto en una fecha: {código}-{AAAAMMDD}-{n}.
# La secuencia es independiente por punto de muestreo.
# DEBE llamarse DENTRO de una transacción que abarque también el INSERT: el lock
# del punto se libera en el COMMIT, no al salir de esta función.
def next_sample_number(sampling_point, code_date):
    SamplePoint.objects.select_for_update().filter(pk=sampling_point.pk).first()
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

`SamplePoint` ya está importado en `models.py:10`. Nótese que la función NO abre su propio `transaction.atomic()`: `number_sample` no tiene constraint único (revisadas las migraciones 0001→0031), así que dos escritores concurrentes sobre el mismo punto —el comando horario y el flujo manual (`core/sampling/forms.py:400` → `SamplingProcess.save()` → `generate_sample_code()`), o dos grupos apuntando al mismo `SamplePoint`— persistirían el duplicado en silencio si el candado se soltara antes del INSERT. Por eso exige que el llamador sostenga la transacción.

**4. Cerrar el flujo manual.** Reemplazar el método `save` de `SamplingProcess` (líneas 99-110) por:

```python
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user

        if not self.number_sample:
            with transaction.atomic():          # abarca lock + SELECT + INSERT
                self.number_sample = self.generate_sample_code()
                return super(SamplingProcess, self).save(*args, **kwargs)
        return super(SamplingProcess, self).save(*args, **kwargs)
```

Anidado dentro del `atomic` de `generate_samplings_for_group` (Task 4), esto degrada a savepoint y el lock se sostiene hasta el COMMIT externo: correcto en ambos flujos. Efecto colateral deseable: la secuencia se hoistiza de facto por lote, porque el lock del punto se sostiene durante todo el `for` de `generate_samplings_for_group`.

**IMPORTANTE — NO eliminar el import `transaction`.** `core/sampling/models.py:4` es `from django.db import models, transaction`; tras eliminar `code_sample_generator` y reescribir `generate_sample_code` sus dos únicos usos desaparecerían, pero el punto 4 lo reintroduce en `save()`. Dejar la línea 4 intacta.

- [ ] **Step 4: Verificar que pasan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_sample_codes -v 2`
Expected: `Ran 6 tests ... OK`

- [ ] **Step 5: Commit**

```bash
git add core/sampling/models.py core/sampling/tests/test_sample_codes.py core/sampling/migrations/0001_initial.py core/sampling/migrations/0005_alter_samplingprocess_number_sample.py core/sampling/migrations/0033_hardening_codigos_y_muestras_por_dia.py
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

    def test_intervalo_coincide_con_la_frecuencia_del_punto(self):
        # Matriz real de FREQUENCY (core/product/forms.py): N = floor(24/f), todos divisores de 24
        for frecuencia, per_day in [(4, 6), (6, 4), (8, 3), (12, 2), (24, 1)]:
            with self.subTest(frecuencia=frecuencia):
                group = build_sampling_group(first_hour='07:00:00', per_day=per_day)
                times = compute_sampling_times(group, TARGET)
                self.assertEqual(len(times), per_day)
                if per_day > 1:
                    self.assertEqual(times[1] - times[0], timedelta(hours=frecuencia))

    def test_intervalo_para_frecuencia_de_8_horas(self):
        group = build_sampling_group(first_hour='07:00:00', per_day=3)  # 24h / 8h = 3
        times = [timezone.localtime(t).time() for t in compute_sampling_times(group, TARGET)]
        self.assertEqual(times, [time(7, 0), time(15, 0), time(23, 0)])

    def test_todos_los_horarios_son_aware(self):
        group = build_sampling_group(per_day=3)
        for t in compute_sampling_times(group, TARGET):
            self.assertFalse(timezone.is_naive(t))
```

Nota sobre el caso "N no divisor de 24": es inalcanzable con datos válidos y por eso no se testea. `number_sampling_day` no es un parámetro libre — la UI lo deriva y lo fija como `readonly` con `Math.floor(24 / sample_frequency)` (`core/sampling/static/form_sampling_group.js:11,29-30`, vía el endpoint `get_sampling_point`), `SamplingGroupForm` solo admite puntos con `sample_frequency` no nulo (`core/sampling/forms.py:331`) y las frecuencias válidas (4/6/8/12/24 h — `core/product/forms.py:10-17`) son todas divisores de 24. La división genérica de la implementación se conserva por robustez ante datos fuera de banda (admin y shell pueden introducir frecuencias no divisoras: `SamplePoint.sample_frequency` es un `SmallIntegerField` sin `choices` a nivel de modelo).

- [ ] **Step 2: Verificar que fallan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_services -v 2`
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

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_services -v 2`
Expected: `Ran 4 tests ... OK`

- [ ] **Step 5: Commit**

```bash
git add core/sampling/services.py core/sampling/tests/test_services.py core/sampling/tests/factories.py
git commit -m "Cálculo de horarios de muestreo distribuidos uniformemente en 24h"
```

---

### Task 3b: Hora local en la serialización de muestras

`toJSON()` renderiza `date_sampling_scheduled` en UTC: con `USE_TZ = True` (`settings.py:125`) y `TIME_ZONE = 'America/Bogota'` (`settings.py:119`), el ORM devuelve datetimes aware en UTC y `.strftime()` sin `timezone.localtime()` imprime UTC. Las horas del ejemplo del spec (07:00, 13:00, 19:00, 01:00) se verían +5h en el listado. No es un comportamiento preexistente uniforme al que los usuarios se hayan acostumbrado, sino una contradicción interna ya viva: `core/sampling/templates/process_sampling/detail_process_sampling.html:102` renderiza el MISMO campo con `{{ object.date_sampling_scheduled|date:"Y-m-d H:i" }}`, y el filtro `date` lleva `expects_localtime=True`, así que el detalle muestra 07:00 y el listado 12:00 para el mismo registro. Esta feature multiplica esa contradicción por N muestras/día/grupo, justo sobre la promesa titular del spec. El patrón correcto ya existe in-repo: `core/condition/views.py:76,226,299` usan `timezone.localtime(...).strftime(...)`.

**Files:**
- Modify: `core/sampling/models.py` (método `SamplingProcess.toJSON`)
- Modify: `core/sampling/views/process_sampling/views.py` (formateo de `date_sampling_scheduled` en el listado)

**Interfaces:**
- Consumes: `SamplingProcess.toJSON()` y la vista de listado de muestras (existentes).
- Produces: `toJSON()['date_sampling_scheduled']` y `toJSON()['date_sampling']` en hora local (`America/Bogota`); listado con `date_sampling_scheduled` en hora local. Sin cambios de firma ni de esquema.

- [ ] **Step 1: Localizar las fechas en `toJSON`**

En `core/sampling/models.py`, dentro de `SamplingProcess.toJSON()` (líneas 91-92), reemplazar:

```python
        item['date_sampling_scheduled'] = self.date_sampling_scheduled.strftime('%Y-%m-%d %H:%M:%S')
        item['date_sampling'] = self.date_sampling.strftime('%Y-%m-%d %H:%M:%S') if self.date_sampling else ''
```

por:

```python
        item['date_sampling_scheduled'] = timezone.localtime(self.date_sampling_scheduled).strftime('%Y-%m-%d %H:%M:%S')
        item['date_sampling'] = timezone.localtime(self.date_sampling).strftime('%Y-%m-%d %H:%M:%S') if self.date_sampling else ''
```

(`timezone` ya está importado en `core/sampling/models.py:6`.)

- [ ] **Step 2: Localizar la fecha en el listado**

En `core/sampling/views/process_sampling/views.py`, añadir a los imports:

```python
from django.utils import timezone
```

(hoy solo se importan `django.utils.decorators` y `django.utils.safestring`; `timezone` NO está importado). Y reemplazar la línea 159:

```python
                        item['date_sampling_scheduled'] = item['date_sampling_scheduled'].strftime('%Y-%m-%d %H:%M')
```

por:

```python
                        item['date_sampling_scheduled'] = timezone.localtime(item['date_sampling_scheduled']).strftime('%Y-%m-%d %H:%M')
```

- [ ] **Step 3: Verificar que no se rompió nada**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling -v 2`
Expected: `Ran 12 tests ... OK` (2 de `test_models` + 6 de `test_sample_codes` + 4 de `test_services`).

- [ ] **Step 4: Commit**

```bash
git add core/sampling/models.py core/sampling/views/process_sampling/views.py
git commit -m "Muestra la programación de muestreo en hora local y no en UTC"
```

Nota: `SamplingAnalysis.toJSON()` (`models.py:177`, `date_analysis`) y `models.py:223` (`analyzed_date`) tienen el mismo defecto; quedan fuera de alcance de esta feature (issue aparte).

---

### Task 4: Generación del lote diario (`generate_samplings_for_group`)

**Files:**
- Modify: `core/sampling/services.py`
- Modify: `core/sampling/forms.py:331` (queryset de `SamplingGroupForm`: solo puntos diarios)
- Modify: `core/sampling/tests/test_services.py` (agregar clase de tests)

**Interfaces:**
- Consumes: `compute_sampling_times` (Task 3), `next_sample_number` (Task 2), `SamplingGenerationLog` (Task 1).
- Produces:
  - Constante `DAILY_PERIODICITY = {'Diaria', 'Diario'}` en `core/sampling/services.py` — única fuente de verdad, consumida también por `core/sampling/forms.py`.
  - `should_skip_group(group: SamplingGroup) -> bool` — True si el grupo está deshabilitado, tiene `number_sampling_day < 1`, el punto está deshabilitado, el punto no tiene código o el punto no es de periodicidad diaria.
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
        # La UI debe mostrar la hora local del spec (07:00), no UTC
        first.refresh_from_db()
        self.assertEqual(first.toJSON()['date_sampling_scheduled'], '2026-07-16 07:00:00')

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

    def test_punto_legacy_diario_si_genera(self):
        point = build_sample_point(code='PM1', periodicity='Diario')  # default histórico del modelo
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertFalse(log.skipped)
        self.assertEqual(log.samples_created, 4)

    def test_punto_no_diario_se_omite(self):
        point = build_sample_point(code='PM1', periodicity='Semanal')
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_grupo_con_cero_muestras_por_dia_se_omite(self):
        group = build_sampling_group(per_day=0)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)
```

`test_punto_legacy_diario_si_genera` fija la trampa legacy, que es el riesgo de regresión más caro: si el check se escribiera como `periodicity != 'Diaria'`, TODOS los puntos con el default histórico `'Diario'` se omitirían y la feature entera dejaría de generar. La aserción sobre `toJSON()` de `test_crea_lote_completo_con_campos_correctos` va sobre una instancia **recargada desde la BD** (`refresh_from_db()`), no la creada en memoria: esta última conserva el tzinfo local y ocultaría el bug de UTC que corrige la Task 3b.

- [ ] **Step 2: Verificar que fallan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_services -v 2`
Expected: ERROR — `ImportError: cannot import name 'generate_samplings_for_group'`

- [ ] **Step 3: Implementar el servicio**

En `core/sampling/services.py`, actualizar imports y agregar:

```python
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingProcess, next_sample_number
```

```python
# Periodicidades que esta feature programa. 'Diario' (masculino) es el default
# histórico del modelo (core/product/models.py:102) y cuenta como diario; las
# choices de la UI usan 'Diaria' (core/product/forms.py:19-23).
DAILY_PERIODICITY = {'Diaria', 'Diario'}


# Regla "sin punto de muestreo no hay muestras": el grupo debe estar habilitado,
# con al menos una muestra por día, y su punto habilitado, con código y diario.
def should_skip_group(group):
    point = group.sampling_point
    return (
        not group.enable_sampling_group
        or group.number_sampling_day < 1
        or not point.enable_point
        or not point.sample_point_code
        or point.periodicity not in DAILY_PERIODICITY
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

La guarda `number_sampling_day < 1` impide un modo de fallo permanente: `number_sampling_day` es `PositiveSmallIntegerField` sin validators de ejecución (`core/sampling/models.py:45`) y admite 0 a nivel de ORM y de Postgres, con lo que `timedelta(hours=24) / 0` lanza `ZeroDivisionError`, que `generate_samplings_for_group` no captura (solo atrapa `IntegrityError`), sube al `except Exception` del comando (Task 5) y produce exit code 1 en CADA corrida horaria, indefinidamente, envenenando el monitoreo. Con la guarda, una configuración inservible cae en el cubo que el spec ya definió (`skipped=True`) en lugar de reventar, y funciona para filas YA existentes en la BD sin importar su origen (admin, shell, POST manipulado, migración de datos).

- [ ] **Step 4: Cerrar la UI — solo puntos diarios seleccionables**

Con el guard solo, el usuario puede configurar un grupo sobre un punto Semanal/Mensual que jamás generará nada y nadie se lo dice (`skipped=True` no hace backfill). `core/sampling/forms.py:331` filtra hoy solo por `enable_point=True, sample_frequency__isnull=False` — sin mirar `periodicity` —, de modo que un punto no diario con frecuencia asignada es seleccionable.

Añadir a los imports de `core/sampling/forms.py`:

```python
from core.sampling.services import DAILY_PERIODICITY
```

(no hay ciclo: `services.py` importa de `core.sampling.models`, no de `forms.py`), y reemplazar la línea 331 por:

```python
        self.fields['sampling_point'].queryset = SamplePoint.objects.filter(enable_point=True, sample_frequency__isnull=False, periodicity__in=DAILY_PERIODICITY)
```

`DAILY_PERIODICITY` se define en un único lugar (`services.py`); nunca duplicarla.

- [ ] **Step 5: Verificar que pasan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_services -v 2`
Expected: `Ran 12 tests ... OK` (4 de `ComputeSamplingTimesTests` + 8 de `GenerateSamplingsForGroupTests`).

- [ ] **Step 6: Verificar que no se rompió nada**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling -v 2`
Expected: `Ran 20 tests ... OK`

- [ ] **Step 7: Commit**

```bash
git add core/sampling/services.py core/sampling/forms.py core/sampling/tests/test_services.py
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
- Produces: comando `python manage.py generate_samplings [--date YYYY-MM-DD] [--dry-run]`. `--date` solo admite fechas pasadas o de hoy. Resumen en stdout `'{N} muestras creadas, {M} días generados, {E} grupos con error'`; lanza `CommandError` (exit code 1) si hubo errores.

- [ ] **Step 1: Escribir los tests que fallan**

`core/sampling/tests/test_command.py`:

```python
from datetime import date
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog, SamplingProcess
from core.sampling.services import generate_samplings_for_group
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

    def test_date_futura_es_rechazada(self):
        build_sampling_group(per_day=2)
        with self.assertRaises(CommandError):
            run(date='2099-01-01')
        self.assertEqual(SamplingGenerationLog.objects.count(), 0)

    def test_log_futuro_no_congela_el_dia_actual(self):
        group = build_sampling_group(per_day=2)
        SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 8, 16))
        run(date='2026-07-16')
        self.assertTrue(
            SamplingGenerationLog.objects.filter(sampling_group=group, target_date=date(2026, 7, 16)).exists()
        )
        self.assertEqual(SamplingProcess.objects.count(), 2)

    def test_error_en_un_grupo_no_bloquea_los_demas(self):
        from unittest import mock

        malo = build_sampling_group(code='MAL', per_day=2)
        build_sampling_group(code='OK', per_day=2)

        real = generate_samplings_for_group

        def falla_solo_el_malo(group, target_date):
            if group.sampling_point.sample_point_code == 'MAL':
                raise RuntimeError('fallo simulado del grupo MAL')
            return real(group, target_date)

        with mock.patch(
            'core.sampling.management.commands.generate_samplings.generate_samplings_for_group',
            side_effect=falla_solo_el_malo,
        ):
            with self.assertRaises(CommandError):
                run(date='2026-07-16')

        creados = SamplingProcess.objects.filter(
            group_sampling__sampling_point__sample_point_code='OK'
        )
        self.assertEqual(creados.count(), 2)
        self.assertEqual(
            SamplingProcess.objects.filter(group_sampling=malo).count(), 0
        )
```

Dos notas sobre estos tests:

- El `mock.patch` de `test_error_en_un_grupo_no_bloquea_los_demas` apunta al símbolo **donde se usa** (el módulo del comando), no donde se define — si se parchea `core.sampling.services.generate_samplings_for_group` el comando seguiría usando su referencia ya importada y el test no inyectaría nada. No sirve inyectar el error con `per_day=0`: la guarda `number_sampling_day < 1` de `should_skip_group` (Task 4) lo convierte en `skipped=True` con exit code 0.
- `test_log_futuro_no_congela_el_dia_actual` es el que demuestra que el guard de `--date` por sí solo no alcanza para datos ya corruptos: hace falta además el bound `target_date__lte=today` del Step 3.

- [ ] **Step 2: Verificar que fallan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_command -v 2`
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
        parser.add_argument('--date', help="Simula la fecha de 'hoy' (YYYY-MM-DD); para pruebas y operación manual. Solo fechas pasadas o de hoy")
        parser.add_argument('--dry-run', action='store_true', help='Reporta lo que se crearía sin escribir en la base de datos')

    def handle(self, *args, **options):
        if options['date']:
            today = datetime.strptime(options['date'], '%Y-%m-%d').date()
            if today > timezone.localdate():
                raise CommandError('--date no puede ser una fecha futura')
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
        last = SamplingGenerationLog.objects.filter(
            sampling_group=group, target_date__lte=today,   # ignora logs de días futuros
        ).aggregate(last=Max('target_date'))['last']
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

Las dos defensas contra el agujero de los logs futuros son complementarias:

- El **guard en `handle`** ataca la causa: un log con `target_date` futuro (escrito por un `--date` manual) crea un agujero permanente y silencioso. Escenario verificado con hoy = 2026-07-16 y logs hasta 07-15: un operador corre `--date 2026-08-16` → `floor` = 07-17, `start` = 07-16 pero `if start < floor: start = floor` ⇒ **07-16 nunca se genera**; y en la corrida real de las 10:10, `last` = 08-16 → `start` = 08-17 > today → el `while day <= today` no itera → 0 muestras, 0 errores, **exit code 0**. El grupo queda sin generar nada durante un mes y el comando reporta éxito. El guard es seguro respecto al reloj de CI: todas las fechas de los tests son <= 2026-07-16, así que solo fallaría en una máquina con reloj anterior a esa fecha.
- El **bound `target_date__lte=today`** en `_process_group` es la red de seguridad para logs futuros YA existentes (datos corruptos anteriores al guard).

- [ ] **Step 4: Verificar que pasan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_command -v 2`
Expected: `Ran 9 tests ... OK`

- [ ] **Step 5: Prueba de humo manual**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py generate_samplings --dry-run`
Expected: líneas `[dry-run] ...` por cada grupo con días pendientes (o solo el resumen si no hay grupos) y exit code 0.

- [ ] **Step 6: Commit**

```bash
git add core/sampling/management/ core/sampling/tests/test_command.py
git commit -m "Comando generate_samplings con catch-up e idempotencia"
```

---

### Task 6: Validación del formulario manual (grupo o punto requerido)

**Files:**
- Modify: `core/sampling/forms.py:381-389` (método `clean` de `SamplingProcessForm`) — anclar por nombre de método; el rango 360-368 es la declaración de clase y el `__init__` (que fija el queryset de `point_sampling`) y NO debe tocarse. Ojo: hay otro `def clean` en `forms.py:311`, de `SamplingAnalysisForm`.
- Create: `core/sampling/tests/test_forms.py`

**Interfaces:**
- Consumes: `SamplingProcessForm` existente (`ValidationError` ya está importado en `forms.py:3`).
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

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_forms -v 2`
Expected: FAIL — `test_sin_grupo_ni_punto_es_invalido` falla porque el formulario es válido sin grupo ni punto (el segundo test debe pasar desde ya).

- [ ] **Step 3: Implementar**

En `core/sampling/forms.py`, dentro de `SamplingProcessForm.clean()` (línea ~381), agregar la validación antes de los `if` existentes:

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

`format_form_errors` (`core/utils.py:17`) ya maneja la clave `__all__`, así que el error no-de-campo se mostrará bien en las vistas Create/Update.

- [ ] **Step 4: Verificar que pasan**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling.tests.test_forms -v 2`
Expected: `Ran 2 tests ... OK`

- [ ] **Step 5: Correr la suite completa de sampling**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling -v 2`
Expected: `Ran 31 tests ... OK` (2 `test_models` + 6 `test_sample_codes` + 12 `test_services` + 9 `test_command` + 2 `test_forms`).

- [ ] **Step 6: Commit**

```bash
git add core/sampling/forms.py core/sampling/tests/test_forms.py
git commit -m "Valida que toda muestra manual tenga grupo o punto de muestreo"
```

---

### Task 7: Infraestructura — supercronic, servicio de compose y documentación de despliegue

**Files:**
- Create: `crontab`
- Create: `.env.example`
- Create: `docs/deploy/scheduler.md`
- Modify: `Dockerfile` (`ARG TARGETARCH` + `ADD` supercronic + `chmod`, tras el `RUN pip install -r requirements.txt` y antes de `COPY . .`)
- Modify: `docker-compose.yml` (servicio `scheduler-luka`, tras el bloque `depends_on` de `web-luka` y antes de la clave raíz `volumes:`)

**Interfaces:**
- Consumes: comando `generate_samplings` (Task 5), `Dockerfile` y `docker-compose.yml` existentes.
- Produces: archivo `crontab` para supercronic, binario de supercronic en la imagen, servicio `scheduler-luka` en el compose y guía de despliegue.

- [ ] **Step 1: Crear el archivo crontab**

`crontab` (raíz del repo):

```
# Generación automática de muestreos: cada hora al minuto 10.
# La primera corrida del día crea el lote completo; las demás son no-ops (idempotente).
10 * * * * python manage.py generate_samplings
```

El `crontab` llega a `/app/crontab` sin trabajo extra: no hay `.dockerignore` y el `COPY . .` del Dockerfile lo incluye.

- [ ] **Step 2: Instalar supercronic en el `Dockerfile`**

En el `Dockerfile` real, insertar entre la línea 51 (`RUN pip install --no-cache-dir -r requirements.txt`) y la línea 54 (`COPY . .`) — esa posición preserva la caché de capas:

```dockerfile
# Supercronic: cron para contenedores (scheduler de muestreos automáticos)
ARG TARGETARCH
ADD https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-${TARGETARCH} /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic
```

Usar `${TARGETARCH}` y NO hardcodear `supercronic-linux-amd64`: la máquina de desarrollo es arm64 (darwin) y el binario amd64 daría `exec format error`. `TARGETARCH` es un build arg predefinido de BuildKit y debe declararse con `ARG TARGETARCH` para poder interpolarse. Sin este step, el `command: supercronic /app/crontab` del servicio daría `exec: "supercronic": not found` en crash-loop (`grep -c supercronic Dockerfile` = 0 hoy).

- [ ] **Step 3: Agregar el servicio `scheduler-luka` al `docker-compose.yml`**

Insertar en `docker-compose.yml` después del bloque `depends_on` de `web-luka` (línea 46) y antes de la clave raíz `volumes:` (línea 48):

```yaml
  scheduler-luka:
    build:
      context: .
      args:
        - MEDIA_URL=${MEDIA_URL}
    command: supercronic /app/crontab
    restart: unless-stopped
    environment:
      - TZ=America/Bogota
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG=${DEBUG}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - BUCKET=${BUCKET}
      - REGION_NAME=${REGION_NAME}
      - MEDIA_URL=${MEDIA_URL}
    depends_on:
      db-luka:
        condition: service_healthy
      web-luka:
        condition: service_started
```

Decisiones, todas verificadas contra el compose real:

- **`build:` replicado en vez de `image:`**: `web-luka` NO declara `image:` (solo `build: context: .`, líneas 17-21), así que no hay imagen nombrada reutilizable, y Compose la autonombra `<proyecto>-web-luka`, nombre que depende del proyecto que genera Dokploy y no es referenciable de forma estable. Nombrar la imagen (p. ej. `image: luka-app:latest` en ambos servicios) introduce una regresión verificada en un servicio que hoy funciona: `docker compose pull` falla con `pull access denied for luka-app, repository does not exist or may require 'docker login'`, mientras que build-sin-`image:` da `Skipped - No image to be pulled`. Replicar el bloque `build:` idéntico (mismo contexto y mismo arg `MEDIA_URL`) es robusto bajo AMBOS pipelines (`pull` y `up -d --build`) y comparte la caché de capas; el costo es una segunda imagen, aceptable.
- **`environment:` en estilo lista con `${}`**, como el resto del compose (Dokploy inyecta su env así). NO usar `env_file: .env`: el compose no lo usa en ningún servicio, falla duro en local (no hay `.env` en la raíz; con `${}` solo hay warnings) e inyectaría variables muertas. Las 7 variables listadas son exactamente las que `settings.py` lee con `config()` sin default. Se omiten deliberadamente los `EMAIL_*`/`USER_MAIL`/`MAIL_PASSWORD`/`PORT`/`MEDIA` que `web-luka` pasa: `settings.py` no define NINGÚN ajuste de email y `MEDIA_URL` está hardcodeada en `settings.py:148` con la línea 149 comentada — son vestigiales.
- **`depends_on: web-luka: condition: service_started`**: las migraciones las aplica únicamente el `CMD` de `web-luka`, y el `command:` del compose reemplaza el CMD del Dockerfile por completo, así que el scheduler NO corre `migrate` (y no debe: dos contenedores compitiendo por el lock de migraciones). En el primer despliegue el scheduler podría dispararse antes de que exista la tabla `SamplingGenerationLog`. `service_started` mitiga; no garantiza que `migrate` haya terminado, pero el reintento horario cubre el resto. NO añadir un healthcheck a `web-luka`: es sobre-ingeniería para una ventana de segundos que la idempotencia ya cubre, e introduce un modo de fallo peor (si el healthcheck se rompe, el scheduler no arranca nunca y en silencio).

- [ ] **Step 4: Crear `.env.example` y documentar la integración**

`.env.example` (raíz del repo, versionado — es plantilla, sin secretos reales):

```
POSTGRES_DB=luka
POSTGRES_USER=luka
POSTGRES_PASSWORD=luka
DATABASE_URL=postgres://luka:luka@db-luka:5432/luka
SECRET_KEY=dev-secret-para-tests
DEBUG=True
MEDIA_URL=/media/
```

`docs/deploy/scheduler.md`:

````markdown
# Scheduler de muestreos automáticos (Dokploy / Docker Compose)

El comando `python manage.py generate_samplings` crea las muestras programadas
del día para cada grupo de muestreo habilitado. Es idempotente y recupera hasta
30 días perdidos, por lo que puede ejecutarse las veces que sea sin duplicar.

## Opción A — Servicio supercronic en el compose (recomendada, portable)

Ya está integrada en este repo. El `Dockerfile` instala el binario de supercronic
(https://github.com/aptible/supercronic) tras las dependencias de Python:

```dockerfile
# Supercronic: cron para contenedores (scheduler de muestreos automáticos)
ARG TARGETARCH
ADD https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-${TARGETARCH} /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic
```

`TARGETARCH` es un build arg predefinido de BuildKit: mantiene la imagen correcta
en amd64 (servidor) y arm64 (desarrollo en darwin). Deuda consciente: el `ADD` no
verifica el SHA1 que recomienda el proyecto supercronic; con `${TARGETARCH}` el
checksum varía por arquitectura.

Y el `docker-compose.yml` levanta el servicio `scheduler-luka` con la misma
definición de build que `web-luka` (no declara `image:`, así que no hay imagen
nombrada que reutilizar; replicar `build:` es lo que funciona bajo
`docker compose pull` y bajo `up -d --build`):

```yaml
  scheduler-luka:
    build:
      context: .
      args:
        - MEDIA_URL=${MEDIA_URL}
    command: supercronic /app/crontab
    restart: unless-stopped
    environment:
      - TZ=America/Bogota
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG=${DEBUG}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - BUCKET=${BUCKET}
      - REGION_NAME=${REGION_NAME}
      - MEDIA_URL=${MEDIA_URL}
    depends_on:
      db-luka:
        condition: service_healthy
      web-luka:
        condition: service_started
```

El scheduler NO corre `migrate`: el `command:` reemplaza el `CMD` del Dockerfile,
y las migraciones las aplica solo `web-luka` (dos contenedores compitiendo por el
lock de migraciones sería peor). En el primer despliegue el reintento horario
cubre la ventana hasta que la tabla `SamplingGenerationLog` exista.

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
  punto deshabilitado, punto no diario o `number_sampling_day < 1` (`skipped=True`).
- Verificación manual sin escribir: `python manage.py generate_samplings --dry-run`.
- `--date` solo acepta fechas pasadas o de hoy. El catch-up avanza desde el
  último log del grupo y no rellena huecos intermedios.
````

- [ ] **Step 5: Verificar la pieza de infraestructura**

La suite de tests no ejercita nada de esto; hay que probarlo aparte.

Run: `docker compose --env-file .env.example config`
Expected: el YAML resuelto incluye `scheduler-luka` con `command: supercronic /app/crontab` y sin errores de sintaxis.

Run: `docker compose run --rm --entrypoint sh scheduler-luka -c 'supercronic -test /app/crontab'`
Expected: `parsed crontab` / `crontab is valid` y exit code 0. Este es el comando que realmente prueba la pieza nueva (que el binario existe en la imagen y que el crontab parsea); sobrescribir el `command` con `python manage.py ...` nunca probaría el scheduler.

- [ ] **Step 6: Verificación final de la suite**

Run: `docker compose run --rm -v "$PWD:/app" web-luka python manage.py test core.sampling -v 2`
Expected: `Ran 31 tests ... OK`

- [ ] **Step 7: Commit**

```bash
git add crontab .env.example docs/deploy/scheduler.md Dockerfile docker-compose.yml
git commit -m "Crontab y guía de despliegue del scheduler de muestreos"
```
