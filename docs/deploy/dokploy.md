# Despliegue en Dokploy

El proyecto se despliega con el stack de `docker-compose.dokploy.yml` (ver también
`docs/deploy/scheduler.md`, que cubre el servicio `scheduler-luka`).

**Requisito previo:** en Dokploy, el *Compose Path* del proyecto debe apuntar a
`docker-compose.dokploy.yml`. El `docker-compose.yml` de la raíz **no sirve para
desplegar**: solo levanta las dependencias de desarrollo local y publica el puerto de la
base.

## El `.env` que Dokploy genera en la ruta del compose

Dokploy escribe las variables del panel en un archivo `.env` que coloca junto al compose
detectado, y le pasa `--env-file` a `docker compose`. El problema es que calcula la
carpeta de destino con:

```js
join(COMPOSE_PATH, appName, "code", composePath)   // composePath = "docker-compose.dokploy.yml"
join(dirname(...), ".env")
```

Con `composePath` apuntando a un **archivo**, `dirname()` devuelve la *ruta del archivo*,
no la carpeta. El resultado es un `touch` sobre una ruta imposible:

```
/bin/sh: 1: cannot create
/etc/dokploy/applications/<app>/code/docker-compose.dokploy.yml/.env:
Directory nonexistent
```

Como `/code` tampoco existe todavía en ese momento, el `touch` no puede crear el
directorio y el despliegue aborta antes de ejecutar `docker compose`. Es un bug de
Dokploy (reportado en `Dokploy/dokploy#2777`), presente al menos hasta `v0.30.7`. En
versiones anteriores (p. ej. `v0.24.0`) funcionaba porque creaban el directorio con
`mkdirSync({ recursive: true })` y luego escribían el archivo.

## Solución: Custom Command

En Dokploy → **Advanced → Command**, sobrescribe el comando para saltar el `--env-file`
roto. Docker Compose lee por defecto el `.env` del directorio actual (que es el `cwd` del
paso de despliegue), así que basta con no pasarle `--env-file`:

```
compose -p <app-name> -f docker-compose.dokploy.yml up -d --build --remove-orphans
```

Reemplaza `<app-name>` por el nombre de proyecto que genera Dokploy (visible en la
pestaña General del proyecto). Dokploy antepone `docker` a este comando.

El comando personalizado **reemplaza** al por defecto por completo; no se le añade nada.
Si más adelante añades flags al comando por defecto (p. ej. `--force-recreate`), tienes
que escribirlos aquí también.

## Alternativas

- **Actualizar Dokploy** a una versión donde `getCreateEnvFileCommand` cree el directorio
  antes del `touch`. Si tu instancia ya está afectada, vuelve a comprobar el log de
  despliegue tras actualizar.
- **Reportar el bug** adjuntando el log completo del despliegue.

## Verificación

Tras aplicar el Custom Command, el despliegue debe superar el paso del `.env` y llegar a
`Docker Compose Deployed: ✅` en los logs. Luego, en los logs de `scheduler-luka`:

```
level=info msg="reaping dead processes"
level=info msg="read crontab: /app/crontab"
```

## Variables de entorno

Las variables del panel de Dokploy siguen haciendo falta: el resto del stack las
referencia con `${VARIABLE}` en `docker-compose.dokploy.yml`. Deben incluir, como mínimo,
`SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`BUCKET`, `REGION_NAME` y `MEDIA_URL` (ver `.env.example`). El Custom Command solo evita
que el `--env-file` mal formado aborte el despliegue; la interpolación `${...}` del
compose sigue resolviéndose contra ese `.env`.
