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
3. **Disparador** — servicio `scheduler` en Docker Compose que ejecuta el comando
   **cada hora** (minuto 10). La primera corrida del día crea todo; las demás son
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
    skipped = models.BooleanField(default=False)  # True = grupo deshabilitado ese día

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

## Lógica de generación

Para el día objetivo `D` de un grupo habilitado con `N = number_sampling_day`:

- Intervalo = `timedelta(hours=24) / N` (admite N no divisores de 24; N=5 →
  cada 4h48m).
- Horarios = `datetime(D, first_hour_sampling) + k × intervalo`, `k = 0 … N-1`,
  interpretados en `America/Bogota` y guardados como datetimes aware
  (`USE_TZ=True`).
- Horarios que cruzan medianoche caen en `D+1` pero pertenecen al lote del día
  `D` (ej.: 4/día desde 07:00 → 07:00, 13:00, 19:00, 01:00 del día siguiente).

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

**Bug actual:** `generate_sample_code()` (`core/sampling/models.py:118`) busca la
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

La función muerta `code_sample_generator()` (`models.py:15`, sin usos) se elimina.

Concurrencia: la generación de cada (grupo, día) ocurre dentro de
`transaction.atomic()`; el insert del log con constraint único actúa como
candado — si otro proceso ya generó ese día, la transacción falla y se ignora.

## Manejo de errores

- Transacción por par (grupo, día): un grupo mal configurado no bloquea a los
  demás, pero un día de un grupo nunca queda a medias.
- Los errores se capturan por grupo, se registran (stdout → logs del
  contenedor) y el comando continúa.
- Resumen final: `X muestras creadas, Y días recuperados, Z grupos con error`.
- Exit code ≠ 0 si hubo al menos un error, para alertas de Dokploy/monitoreo.

## Infraestructura (Docker Compose / Dokploy)

El repo aún no tiene `Dockerfile`/`docker-compose.yml`; esta feature aporta la
pieza del scheduler para integrarla al compose del despliegue:

```yaml
scheduler:
  image: <misma imagen de la app>
  command: supercronic /app/crontab
  environment:
    TZ: America/Bogota
    # mismas variables de entorno de la app (DATABASE_URL, SECRET_KEY, ...)
```

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

1. **Horarios**: distribución uniforme; N no divisor de 24; cruce de medianoche.
2. **Idempotencia**: ejecutar el comando dos veces el mismo día → cero duplicados.
3. **Catch-up**: 3 días sin correr → se crean los 3 días; el tope de 30 días se
   respeta.
4. **Grupos deshabilitados**: no generan, log con `skipped=True`; al rehabilitar
   no hay backfill del período deshabilitado.
5. **Códigos**: secuencia independiente por punto (regresión del bug);
   continuidad con muestras manuales y automáticas el mismo día; fecha del
   código = día programado en catch-up.
6. **Errores**: un grupo inválido no impide procesar los demás; exit code ≠ 0.
7. **Punto de muestreo requerido**: punto deshabilitado o sin código → log con
   `skipped=True` y cero muestras, sin backfill al rehabilitarlo; el formulario
   manual rechaza muestras sin grupo ni punto.

## Fuera de alcance

- Backfill histórico anterior al despliegue de la feature.
- Notificaciones (correo/alertas) por muestras atrasadas.
- UI para ver los logs de generación (accesibles vía admin de Django).
- Dockerfile y compose completos del despliegue (solo se especifica el servicio
  scheduler).
