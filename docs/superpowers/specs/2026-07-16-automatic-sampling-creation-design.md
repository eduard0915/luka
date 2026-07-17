# Diseño: Creación Automática de Muestreos

**Fecha:** 2026-07-16
**Estado:** Aprobado en sesión de brainstorming

## Problema

Hoy los registros `SamplingProcess` se crean solo manualmente mediante formulario.
El modelo `SamplingGroup` ya define la configuración de un cronograma (punto de
muestreo, `first_hour_sampling`, `number_sampling_day`, `enable_sampling_group`),
pero nada crea las muestras programadas automáticamente.

Se necesita un mecanismo recurrente que cree las muestras del día para cada grupo
habilitado, resistente a caídas del servidor y sin duplicar registros.

## Decisiones tomadas

| Tema | Decisión |
|------|----------|
| Distribución de horarios | Uniforme en 24h: intervalo = 24h ÷ `number_sampling_day`, iniciando en `first_hour_sampling` |
| Origen del intervalo | `number_sampling_day`, derivado en la UI de `SamplePoint.sample_frequency` (`Math.floor(24 / frecuencia)`). El generador consume N de la BD; no revalida ni recalcula la frecuencia |
| Periodicidad cubierta | Solo puntos diarios. `'Diaria'` (choice de la UI) y `'Diario'` (default histórico del modelo) cuentan ambos como diario; `'Semanal'` y `'Mensual'` se omiten con `skipped=True` y se siguen atendiendo con muestras manuales |
| Momento de creación | Todo el día por adelantado (lote diario) |
| Mecanismo de scheduling | Management command de Django + contenedor cron (supercronic) en Docker Compose. Se descartaron pg_cron (lógica de negocio en SQL, fuera del ORM/señales) y django-q2/Celery (infraestructura innecesaria para un job diario) |
| Despliegue | Dokploy con Docker Compose |
| `type_sampling` de muestras automáticas | Siempre `'En Proceso'` |
| Recuperación ante fallos | Catch-up de días completos perdidos (tope 30 días), idempotente |

## Arquitectura

Tres piezas con responsabilidades separadas:

1. **Servicio de dominio** — `core/sampling/services.py`
   - `generate_samplings_for_group(group, target_date)`: calcula horarios y crea
     los `SamplingProcess` de un grupo para un día. Función pura de negocio,
     testeable de forma aislada.
2. **Management command** — `core/sampling/management/commands/generate_samplings.py`
   - Itera todos los grupos, aplica catch-up e idempotencia, maneja errores por
     grupo, imprime resumen.
   - Flags: `--date YYYY-MM-DD` (simular "hoy", usado por tests y operación
     manual) y `--dry-run` (reporta sin escribir).
3. **Disparador** — servicio `scheduler-luka` en Docker Compose que ejecuta el
   comando **cada hora** (minuto 10). La primera corrida del día crea todo; las demás son
   no-ops por idempotencia. La frecuencia horaria cubre el caso "servidor caído a
   medianoche, recuperado durante el día" sin esperar al día siguiente.

El comando es la única lógica; el disparador es intercambiable (supercronic,
Scheduled Tasks de Dokploy, cron del host) sin tocar código.

## Modelo de datos

Tabla nueva (app `sampling`), siguiendo las convenciones existentes
(`BaseModel`, PK UUID, `db_table` en PascalCase):

```python
class SamplingGenerationLog(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sampling_group = models.ForeignKey(SamplingGroup, on_delete=models.CASCADE)
    target_date = models.DateField(verbose_name='Día Generado')
    samples_created = models.PositiveSmallIntegerField(default=0)
    skipped = models.BooleanField(default=False)  # True = grupo/punto no generable ese día

    class Meta:
        db_table = 'SamplingGenerationLog'
        constraints = [
            models.UniqueConstraint(
                fields=['sampling_group', 'target_date'],
                name='unique_group_target_date',
            )
        ]
```

La restricción única `(sampling_group, target_date)` garantiza idempotencia a
nivel de base de datos: aunque dos procesos corran a la vez, un día de un grupo
solo puede generarse una vez.

### Regla: sin punto de muestreo no se crean muestras

- **Flujo automático:** un grupo solo genera muestras si su `sampling_point`
  está habilitado (`enable_point=True`) y tiene `sample_point_code` no vacío.
  Si el punto está deshabilitado o sin código, el día se registra con
  `skipped=True` — misma semántica que un grupo deshabilitado: al rehabilitar
  el punto NO se rellena el período (deshabilitado ≠ servidor caído).
- **Periodicidad diaria:** además, el punto debe ser de periodicidad diaria y
  el grupo debe tener `number_sampling_day >= 1`; en caso contrario el día se
  registra con `skipped=True`. Los puntos `'Semanal'` y `'Mensual'` quedan
  fuera del flujo automático y se siguen atendiendo con muestras manuales.
  **Trampa:** `'Diario'` (masculino) es el default histórico del modelo
  (`core/product/models.py:102`) y cuenta como diario, aunque las choices de la
  UI usen `'Diaria'` (`core/product/forms.py:19-23`). El check es una whitelist
  (`{'Diaria', 'Diario'}`, definida en un único lugar); un `periodicity != 'Diaria'`
  ingenuo omitiría TODOS los puntos legacy y la feature no generaría nada.
- La guarda `number_sampling_day >= 1` no es cosmética: el campo es
  `PositiveSmallIntegerField` sin validators (`core/sampling/models.py:45`) y
  admite 0 a nivel de ORM y de Postgres, con lo que `24h ÷ 0` reventaría el
  comando con `ZeroDivisionError` en cada corrida horaria. Una configuración
  inservible cae en el cubo de `skipped=True` en vez de envenenar el monitoreo.
  El modelo pasa además a declarar `MinValueValidator(1)` sobre ese campo como
  defensa en profundidad (admin y POST manipulados); la guarda de ejecución vive
  en el servicio y cubre también las filas ya existentes en la BD.
- **UI:** `SamplingGroupForm` deja de ofrecer puntos no diarios en su queryset
  (`core/sampling/forms.py:331`, hoy filtra solo por `enable_point=True` y
  `sample_frequency__isnull=False`), para que no puedan crearse grupos muertos:
  `skipped=True` no hace backfill y nadie avisaría al usuario.
- **Flujo manual:** `SamplingProcessForm` valida que se especifique
  `group_sampling` o `point_sampling`. Hoy ambos campos son opcionales y el
  error solo aparece después como `ValueError` al generar el código; pasa a ser
  un error de validación del formulario.

### Reglas de catch-up

- Para cada grupo se procesan los días desde *el día siguiente al último log de
  ese grupo* hasta hoy inclusive. Tope de seguridad: 30 días hacia atrás
  (constante en el comando, no un setting configurable).
- Grupo **deshabilitado** en el momento de la corrida: se escribe log con
  `skipped=True` y `samples_created=0`. Al rehabilitarlo NO se rellena el
  período deshabilitado (deshabilitado ≠ servidor caído).
- Grupo **sin ningún log** (primer despliegue o grupo nuevo): se empieza desde
  hoy, sin backfill histórico.
- El flag `--date` solo admite fechas pasadas o de hoy: una fecha futura
  escribiría un log adelantado que **congelaría al grupo**, porque el catch-up
  avanza desde el último log del grupo y no rellena huecos intermedios (el
  comando reportaría éxito con cero muestras durante todo el período saltado).
  Una fecha futura se rechaza con `CommandError`. Como red de seguridad para
  logs futuros ya existentes, el cálculo del último log ignora los que tengan
  `target_date` posterior a hoy.

## Lógica de generación

Para el día objetivo `D` de un grupo habilitado con `N = number_sampling_day`:

- Intervalo = `timedelta(hours=24) / N`. `number_sampling_day` no es un
  parámetro libre: la UI lo deriva y lo fija como `readonly` con
  `Math.floor(24 / sample_frequency)`
  (`core/sampling/static/form_sampling_group.js:11,29`, vía el endpoint
  `get_sampling_point`), y `SamplingGroupForm` solo admite puntos con
  `sample_frequency` no nulo (`core/sampling/forms.py:331`). Como las
  frecuencias válidas (4/6/8/12/24 h — `core/product/forms.py:10-17`) son todas
  divisores de 24, el intervalo `24h ÷ N` siempre coincide exactamente con la
  frecuencia declarada del punto. Se conserva la división genérica por robustez
  ante datos fuera de banda: `SamplePoint.sample_frequency` es un
  `SmallIntegerField` sin `choices` a nivel de modelo
  (`core/product/models.py:97`), por lo que admin y shell pueden introducir
  frecuencias no divisoras.
- Horarios = `datetime(D, first_hour_sampling) + k × intervalo`, `k = 0 … N-1`,
  interpretados en `America/Bogota` y guardados como datetimes aware
  (`USE_TZ=True`).
- Horarios que cruzan medianoche caen en `D+1` pero pertenecen al lote del día
  `D` (ej.: 4/día desde 07:00 → 07:00, 13:00, 19:00, 01:00 del día siguiente).
- Esas horas son las que debe ver el usuario. La serialización actual
  (`SamplingProcess.toJSON()` y el listado de muestras) usa `.strftime()` sobre
  el datetime aware que devuelve el ORM, que está en UTC, así que imprimiría
  12:00 donde el spec promete 07:00; el detalle, en cambio, ya localiza con el
  filtro `|date:`. No es una convención preexistente sino una contradicción viva
  que esta feature multiplicaría por N muestras/día/grupo: la serialización pasa
  a usar `timezone.localtime()`, el patrón que ya existe en
  `core/condition/views.py`.

Cada `SamplingProcess` creado:

| Campo | Valor |
|-------|-------|
| `group_sampling` | el grupo |
| `type_sampling` | `'En Proceso'` |
| `date_sampling_scheduled` | horario calculado |
| `automatic_sampling` | `True` |
| `status_sampling` | `'Programada'` (default del modelo) |
| `number_sample` | ver "Códigos de muestra" |
| `user_creation` | nulo — el comando corre sin usuario web (crum devuelve `None`); `automatic_sampling=True` identifica el origen |

## Códigos de muestra (corrección de bug incluida)

**Bug actual:** `generate_sample_code()` (`core/sampling/models.py:128`) busca la
última muestra del día **globalmente** y compara su punto con el actual. Con
varios puntos intercalados produce códigos duplicados (A-1, B-1, luego A otra
vez → vuelve a A-1). La creación masiva automática lo dispararía de inmediato.

**Nueva lógica** (reemplaza a la actual; la usan el flujo manual y el automático):

```
prefijo   = f'{codigo_punto}-{AAAAMMDD}'
existentes = SamplingProcess.objects.filter(number_sample__startswith=prefijo + '-')
siguiente  = max(sufijo numérico de existentes) + 1   # 1 si no hay
```

Cambios de semántica deliberados:

1. La secuencia es **por punto de muestreo** (corrige el bug).
2. Para muestras generadas automáticamente, la fecha del código es la del **día
   del lote** (`target_date`), no la del día en que corrió el comando ni la
   fecha calendario del horario: la muestra de 01:00 que cruza a `D+1` lleva la
   fecha `D`, igual que el resto de su lote. El flujo manual sigue usando la
   fecha de hoy.

**Invariante de longitud:**
`max_length(number_sample) >= max_length(sample_point_code) + 15`
(1 separador + 8 de fecha + 1 separador + 5 del consecutivo). Hoy el campo es
`max_length=25` (`core/sampling/models.py:74`) mientras `sample_point_code`
admite 30 (`core/product/models.py:95`), así que cualquier código de punto de
más de 13-14 caracteres desborda con `DataError` — que **no** es subclase de
`IntegrityError`, escaparía del manejo por (grupo, día) y dejaría al comando
fallando en cada corrida horaria. `number_sample` pasa por tanto a 45 (= 30 + 15).
La cota se deriva del límite **declarado** del campo, no del dato del día: la UI
expone `sample_point_code` como `TextInput` sin validadores. Si se amplía
`sample_point_code`, `number_sample` debe revisarse en el mismo cambio — es
exactamente lo que faltó en la migración 0005, donde se pasó de 15 a 25 a ojo.
El consecutivo real nunca pasa de 2 dígitos porque `sample_frequency` es horaria
(máx. 24 muestras por punto y día); los 5 dígitos son holgura.

**Eliminación de la función muerta:** `code_sample_generator()`
(`models.py:16`) se elimina. No tiene usos en código de producción, pero las
migraciones históricas 0001 (`0001_initial.py:3,47`) y 0005
(`0005_alter_samplingprocess_number_sample.py:3,17`) la referencian como
`default` del campo, y el `MigrationLoader` de Django importa TODAS las
migraciones de la app en cualquier comando que toque el grafo: borrarla a secas
produce `AttributeError` y revienta `migrate`, `makemigrations`, `manage.py test`
y el arranque del contenedor. Ambas migraciones deben despojarse de esa
referencia **antes** de borrar la función, en el mismo commit. Es seguro: la
migración 0006 ya hace un `AlterField` al mismo campo sin default y el modelo
tampoco lo declara, así que el estado final del grafo no cambia; y `default` es
de aplicación, no de esquema, de modo que el efecto en la BD es nulo.

**Concurrencia:** la generación de cada (grupo, día) ocurre dentro de
`transaction.atomic()`; el insert del log con constraint único actúa como candado
del par (grupo, día) — si otro proceso ya generó ese día, la transacción falla y
se ignora. Ese `except IntegrityError` se acota al choque con
`unique_group_target_date` (se reconsulta el log): cualquier otra violación —una FK
a un grupo borrado a media generación, por ejemplo— es un error real y debe escalar
al comando. Si se atrapara toda `IntegrityError`, el lote se perdería y el cron
reportaría éxito con exit code 0.

**Candado de la secuencia del código:** un `select_for_update()` **sobre todos los
`SamplePoint` que comparten el código**, no sobre la fila del punto. La distinción
es el punto fino: `sample_point_code` no tiene `unique=True`
(`core/product/models.py:95`) y dos puntos de productos distintos pueden usar
`'PM1'` legítimamente; la secuencia se calcula sobre el *namespace del código*
(`number_sample__startswith='PM1-AAAAMMDD-'`), así que compartir contador entre esos
puntos es lo correcto —es justo lo que evita que ambos emitan `PM1-…-1`—, pero el
candado debe cubrir ese mismo namespace. Bloquear solo la fila del punto no
serializa a dos escritores sobre puntos distintos que comparten código: ambos leen
el mismo máximo y persisten el duplicado sin error, porque `number_sample` tampoco
tiene constraint único. El `order_by('pk')` da un orden de adquisición estable y
evita deadlocks.

El candado debe sostenerse **hasta el COMMIT del INSERT** de la muestra: por eso la
función que calcula el siguiente número no abre transacción propia (exige que el
llamador sostenga la que abarca el INSERT) y `SamplingProcess.save()` envuelve
generación e inserción en un único `atomic()`. Esto NO es «restaurar» el bloqueo
previo: el `select_for_update()` que había en `generate_sample_code()` nunca
protegió el INSERT, porque su `atomic()` cerraba antes de que `save()` llamara a
`super().save()`. El disparador real de la carrera es el cron horario corriendo
mientras un usuario da de alta muestras por el formulario: ambos caminos llegan a la
misma función.

`number_sample` lleva `db_index=True`: el filtro por prefijo sin índice es un seq
scan de toda la tabla, y se paga con el candado tomado. Django crea además el índice
`_like` con `varchar_pattern_ops`, que es el único que sirve para `LIKE 'prefijo%'`
con el collation `en_US.utf8` de la base.

## Manejo de errores

- Transacción por par (grupo, día): un grupo mal configurado no bloquea a los
  demás, pero un día de un grupo nunca queda a medias.
- Los errores se capturan por grupo, se registran (stdout → logs del
  contenedor) y el comando continúa.
- Resumen final: `X muestras creadas, Y días recuperados, Z grupos con error`.
- Exit code ≠ 0 si hubo al menos un error, para alertas de Dokploy/monitoreo.

## Infraestructura (Docker Compose / Dokploy)

El repo ya incluye `Dockerfile` (`FROM python:3.12-slim-bookworm`, `WORKDIR /app`,
`CMD python manage.py migrate && gunicorn luka.wsgi:application ...`) y
`docker-compose.yml` (servicios `db-luka` sobre postgres:16-alpine con
healthcheck, y `web-luka` con `build: context: .`). Esta feature agrega el
binario de supercronic a ese Dockerfile y el servicio `scheduler-luka` a ese
compose:

```dockerfile
# Supercronic: cron para contenedores (scheduler de muestreos automáticos)
ARG TARGETARCH
ADD https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-${TARGETARCH} /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic
```

Va entre el `RUN pip install -r requirements.txt` y el `COPY . .`, para preservar
la caché de capas. `${TARGETARCH}` (build arg predefinido de BuildKit, hay que
declararlo con `ARG` para interpolarlo) en vez de hardcodear `amd64`: la máquina
de desarrollo es arm64 y ese binario daría `exec format error`. El `crontab`
llega a `/app/crontab` sin trabajo extra — no hay `.dockerignore` y el `COPY . .`
lo incluye. Deuda consciente: el `ADD` no verifica el SHA1 que recomienda
supercronic, porque el checksum varía por arquitectura.

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

Decisiones del bloque, todas verificadas contra el compose real:

- **`build:` replicado en vez de `image:`**: `web-luka` no declara `image:`, así
  que no hay imagen nombrada reutilizable y Compose la autonombra con el nombre
  de proyecto que genera Dokploy, no referenciable de forma estable. Nombrar la
  imagen en ambos servicios introduce una regresión verificada en un servicio
  que hoy funciona: `docker compose pull` falla con `pull access denied`,
  mientras que build-sin-`image:` da `Skipped - No image to be pulled`. Replicar
  el bloque `build:` idéntico es robusto bajo ambos pipelines (`pull` y
  `up -d --build`) y comparte la caché de capas; el costo es una segunda imagen.
- **`environment:` en estilo lista con `${}`**, como el resto del compose
  (Dokploy inyecta su env así). NO `env_file: .env`: ningún servicio lo usa y
  falla duro en local, donde no hay `.env` en la raíz. Las variables listadas son
  exactamente las que `settings.py` lee con `config()` sin default; se omiten
  los `EMAIL_*`/`USER_MAIL`/`MAIL_PASSWORD`/`PORT`/`MEDIA` que `web-luka` pasa
  porque `settings.py` no define ningún ajuste de email y son vestigiales.
- **`depends_on: web-luka: condition: service_started`**: las migraciones las
  aplica únicamente el `CMD` de `web-luka`, y el `command:` del compose reemplaza
  al CMD del Dockerfile, así que el scheduler no corre `migrate` — y no debe:
  dos contenedores compitiendo por el lock de migraciones. `service_started`
  mitiga la ventana del primer despliegue (el scheduler podría dispararse antes
  de que exista la tabla `SamplingGenerationLog`); no la elimina, pero el
  reintento horario cubre el resto. Deliberadamente **sin** healthcheck en
  `web-luka`: es sobre-ingeniería para una ventana de segundos que la
  idempotencia ya cubre, e introduce un modo de fallo peor (si el healthcheck se
  rompe, el scheduler no arranca nunca y en silencio).

Archivo `crontab` en la raíz del repo:

```
10 * * * * python manage.py generate_samplings
```

Alternativa sin contenedor extra: las **Scheduled Tasks nativas de Dokploy**
ejecutando el mismo comando en el contenedor de la app. El comando no cambia;
solo el disparador.

## Plan de testing

Tests en `core/sampling/tests/` (ejecutados con `manage.py test`), inyectando
la fecha vía `--date` (sin mocks de reloj ni dependencias nuevas):

1. **Horarios**: distribución uniforme; el intervalo coincide con la frecuencia
   declarada del punto (matriz real 4/6/8/12/24 h); cruce de medianoche.
2. **Idempotencia**: ejecutar el comando dos veces el mismo día → cero duplicados.
3. **Catch-up**: 3 días sin correr → se crean los 3 días; el tope de 30 días se
   respeta; un `--date` futuro se rechaza y un log con `target_date` futuro ya
   existente no congela el día actual.
4. **Grupos deshabilitados**: no generan, log con `skipped=True`; al rehabilitar
   no hay backfill del período deshabilitado.
5. **Códigos**: secuencia independiente por punto (regresión del bug);
   continuidad con muestras manuales y automáticas el mismo día; fecha del
   código = día programado en catch-up; un `sample_point_code` de 30 caracteres
   (el máximo del campo) no desborda `number_sample`, y el invariante de longitud
   queda atado en un test que compara los `max_length` de ambos campos — no basta
   con un `assertLessEqual(len(...), 45)`, que es tautológico si el INSERT no
   lanzó. Las fábricas usan códigos de 3 caracteres, así que sin este test el
   desbordamiento pasaría verde y reventaría en producción.
6. **Errores**: un grupo inválido no impide procesar los demás; exit code ≠ 0.
7. **Punto de muestreo y periodicidad**: punto deshabilitado, sin código o de
   periodicidad no diaria (`'Semanal'`/`'Mensual'`) → log con `skipped=True` y
   cero muestras, sin backfill al rehabilitarlo; un punto legacy `'Diario'` **sí**
   genera (es la regresión más cara: la feature entera dejaría de generar); un
   grupo con `number_sampling_day = 0` se omite en vez de reventar; el formulario
   manual rechaza muestras sin grupo ni punto.
8. **Hora local**: la serialización de una muestra recargada desde la BD devuelve
   la hora local del ejemplo (07:00), no UTC. La aserción debe correr sobre una
   instancia con `refresh_from_db()`: la creada en memoria conserva el tzinfo
   local y ocultaría el bug.

## Fuera de alcance

- Backfill histórico anterior al despliegue de la feature.
- Notificaciones (correo/alertas) por muestras atrasadas.
- UI para ver los logs de generación (accesibles vía admin de Django).
- Reescribir el `Dockerfile`/`docker-compose.yml` más allá de las dos adiciones
  de esta feature (binario de supercronic y servicio `scheduler-luka`).
- Periodicidades Semanal y Mensual: esta feature solo programa puntos diarios;
  esos puntos se siguen atendiendo con muestras manuales.
- Normalizar el valor legacy `'Diario'` en los datos existentes y alinear el
  default de `SamplePoint.periodicity` (`core/product/models.py:102`) con las
  choices de la UI. Deuda consciente y deliberada: esta feature convive con
  ambos valores tratándolos como diarios. Migrar los datos y tocar el default del
  modelo es un cambio con radio propio, ajeno a la generación de muestreos.
- El bug de `SamplePointUpdateForm` (`core/product/forms.py:157-167`), que omite
  `periodicity` de `Meta.fields` pero expone `sample_frequency` sin `clean()`:
  en edición el toggle de JS no encuentra el select y queda inerte, dejando la
  frecuencia editable. Es la causa raíz de que un punto no diario pueda tener
  frecuencia asignada. El arreglo real es un `clean()` en ese form que fuerce
  `sample_frequency=None` cuando el punto no sea diario — la validación no puede
  vivir solo en JS. Issue aparte.
- `UniqueConstraint` sobre `number_sample`: es la única garantía dura contra
  códigos duplicados, pero exige auditar y limpiar los duplicados que el bug
  global de `generate_sample_code()` ya pudo generar en producción, y obliga a
  distinguir su `IntegrityError` del que hoy significa «día ya generado» (que
  devolvería `None` y perdería el lote en silencio). Issue aparte.
- El mismo defecto de UTC en `SamplingAnalysis.toJSON()` (`date_analysis`) y en
  `analyzed_date`: esta feature solo corrige la serialización de
  `SamplingProcess`, que es la que toca. Issue aparte.
- El manejador de errores de `SamplingProcessForm.save()` (`core/sampling/forms.py`):
  reasigna `data` a la instancia con `data = form.save(commit=False)` y luego el
  `except` hace `data['error'] = str(e)`, que lanza `TypeError` y enmascara la
  excepción original. Preexistente y ajeno a la generación automática; la corrección
  del `clean()` de esta feature elimina el camino que más lo disparaba. Issue aparte.
