# Scheduler de muestreos automáticos

El comando `python manage.py generate_samplings` crea las muestras programadas
del día para cada grupo de muestreo habilitado. Es idempotente y recupera hasta
30 días perdidos, por lo que puede ejecutarse las veces que sea sin duplicar.

En el despliegue lo dispara el servicio `scheduler-luka` del `docker-compose.yml`,
que corre supercronic con el `crontab` de la raíz del repo: cada hora al minuto 10.
La primera corrida del día crea el lote completo; las demás son no-ops. La
frecuencia horaria cubre el caso "servidor caído a medianoche, recuperado durante
el día" sin esperar al día siguiente.

## Qué genera

Para cada `SamplingGroup` habilitado cuyo punto de muestreo esté habilitado, tenga
código y sea de periodicidad diaria, crea `number_sampling_day` muestras repartidas
uniformemente en 24 h desde `first_hour_sampling` (el intervalo coincide con la
frecuencia declarada del punto). Las muestras quedan en estado `Programada` con
`automatic_sampling=True`.

Se omiten (quedan registradas con `skipped=True` y cero muestras) los grupos
deshabilitados, con `number_sampling_day` en 0, o cuyo punto esté deshabilitado,
sin código, o con periodicidad Semanal/Mensual. Rehabilitar después NO rellena el
período omitido.

## Piezas

| Pieza | Ubicación |
|-------|-----------|
| Lógica de negocio | `core/sampling/services.py` |
| Comando | `core/sampling/management/commands/generate_samplings.py` |
| Programación | `crontab` (raíz del repo) |
| Servicio | `scheduler-luka` en `docker-compose.yml` |
| Binario de cron | supercronic, instalado en el `Dockerfile` |
| Auditoría | tabla `SamplingGenerationLog` (visible en el admin de Django) |

## Despliegue en Dokploy

El servicio `scheduler-luka` ya está en el `docker-compose.yml`: se despliega solo
con el resto del stack. Requisitos:

1. Las variables de entorno del proyecto en Dokploy deben incluir las mismas que
   usa `web-luka` (`SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `AWS_ACCESS_KEY_ID`,
   `AWS_SECRET_ACCESS_KEY`, `BUCKET`, `REGION_NAME`, `MEDIA_URL`). Ver `.env.example`.
2. El scheduler NO corre `migrate`: eso lo sigue haciendo únicamente `web-luka`
   (dos contenedores compitiendo por el lock de migraciones sería un problema).
   Por eso depende de `web-luka` con `condition: service_started`.
3. Tras el primer despliegue, verificar en los logs del contenedor `scheduler-luka`
   que supercronic arrancó y que a los pocos minutos aparece la línea de resumen.

Alternativa sin contenedor extra: una **Scheduled Task** de Dokploy sobre el
servicio de la app con el comando `python manage.py generate_samplings` y la
programación `10 * * * *`. El comando es el mismo; solo cambia el disparador.

## Verificación

```bash
# El compose es válido y el scheduler está declarado
docker compose --env-file .env.example config

# El binario existe en la imagen y el crontab parsea
docker compose run --rm --entrypoint sh scheduler-luka -c 'supercronic -test /app/crontab'

# Qué se crearía hoy, sin escribir nada
docker compose run --rm web-luka python manage.py generate_samplings --dry-run
```

## Monitoreo

- El comando termina con exit code 1 si algún grupo falló (los demás se procesan
  igual); los detalles quedan en stderr, visibles en los logs del contenedor.
- Cada día generado queda auditado en `SamplingGenerationLog`, incluidos los días
  omitidos (`skipped=True`).
- `--date AAAA-MM-DD` fuerza la fecha de "hoy" y solo acepta fechas pasadas o de
  hoy: una fecha futura escribiría un log adelantado que congelaría al grupo (el
  catch-up avanza desde el último log del grupo y no rellena huecos intermedios).

## Deuda conocida

- El `ADD` de supercronic en el `Dockerfile` no verifica el checksum SHA1 que
  recomienda el proyecto (varía por arquitectura al usar `${TARGETARCH}`).
- `number_sample` no tiene constraint único en base de datos. La secuencia está
  protegida por un `select_for_update()` sobre el punto de muestreo, pero la
  garantía dura exigiría auditar antes los duplicados que el bug anterior de
  `generate_sample_code()` pudo dejar en producción.
