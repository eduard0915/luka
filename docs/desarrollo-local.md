# Correr el proyecto en local sin Docker

Guía verificada en macOS (Apple Silicon) contra este repo. Para correrlo con Docker
ver `docs/deploy/scheduler.md` y el `docker-compose.yml`.

El servidor Django corre en tu máquina (con recarga automática), y sus dependencias —la
base de datos y el cron de muestreos— en Docker. Así la base es la misma versión que
producción (`postgres:16-alpine`), es desechable y no te deja un servicio permanente
instalado.

## 1. Dependencias del sistema

```bash
brew install python@3.13 cairo pkg-config
```

`pkg-config` no es opcional: sin él la instalación de `pycairo` falla con
`error: metadata-generation-failed` porque no encuentra las cabeceras de cairo. Es el
error más común al montar este proyecto desde cero.

Sobre la versión de Python: la imagen de Docker usa 3.12, pero el proyecto corre bien
en 3.13 (verificado: las 39 pruebas de `core.sampling` pasan). Evita 3.14 por ahora —
varias dependencias compiladas aún no publican wheels para esa versión.

## 2. Levantar las dependencias (base de datos y cron)

Primero el `.env` de la raíz, que es el que lee docker compose para interpolar las
`${VARIABLES}` del archivo (ver la sección 4 sobre los dos `.env`):

```bash
cp .env.example .env
```

Y arriba:

```bash
docker compose up -d
```

Eso levanta:

- **`db-luka`** — PostgreSQL 16, publicado en `127.0.0.1:5432` para que el Django del
  host lo alcance. El rol y la base se crean solos con las variables `POSTGRES_*`, ya
  con permiso para crear la base `test_luka` que el runner de pruebas necesita.
- **`scheduler-luka`** — el cron de muestreos, con el código del host montado, así que
  ejecuta lo que estás editando.

Comandos útiles:

```bash
docker compose logs -f scheduler-luka   # ver el cron disparar
docker compose ps                       # estado
docker compose down                     # parar (con -v además borra los datos)
```

`docker-compose.yml` es solo para esto. El despliegue usa `docker-compose.dokploy.yml`,
que lleva el stack completo y no publica el puerto de la base.

## 3. Entorno virtual e instalación

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`.venv` está en el `.gitignore`. La instalación compila `pycairo` desde fuente, así que
la primera vez tarda un par de minutos.

## 4. Variables de entorno

Crea el archivo **`luka/.env`** (no en la raíz — ver la nota de abajo):

```
SECRET_KEY=dev-local-no-usar-en-produccion
DEBUG=True
DATABASE_URL=postgres://luka:luka@localhost:5432/luka
MEDIA_URL=/media/
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
BUCKET=local
REGION_NAME=us-east-1
```

Hay dos trampas en cómo este proyecto lee la configuración, y las dos muerden:

**Ningún valor puede quedar vacío.** El proyecto usa `django-decouple`, que resuelve
cada variable como `valor_del_archivo or os.environ[VARIABLE]`. Un valor vacío es
falsy, así que cae a la variable de entorno y, si tampoco existe, revienta al arrancar
con `KeyError: 'AWS_ACCESS_KEY_ID'`. En local pon `local` como relleno; nunca dejes la
clave en blanco.

**El archivo `.env` gana sobre las variables de entorno**, al revés de lo que casi todo
el mundo espera (`python-decouple` estándar hace lo contrario). De ahí sale la
convención de dos archivos:

| Archivo | Lo lee | Para qué |
|---------|--------|----------|
| `luka/.env` | el Django del host | tu configuración local (`DATABASE_URL` a `localhost`) |
| `.env` (raíz) | docker compose | interpolar las `${VARIABLES}` del compose |

decouple busca desde `luka/settings.py` hacia arriba, así que encuentra `luka/.env`
primero y la raíz solo si aquel no existe. Manteniéndolos separados, el host y los
contenedores no se pisan con el host de la base. Ambos están en el `.gitignore`, y el
`.dockerignore` impide que cualquiera entre en la imagen (si entrara, sobrescribiría en
silencio el `SECRET_KEY` y el `DEBUG` del despliegue).

Detalle que evita una confusión: el `scheduler-luka` monta el repo, así que ve tu
`luka/.env` con `localhost` — que dentro del contenedor sería él mismo. No es problema:
el compose le pasa `DATABASE_URL` apuntando a `db-luka`, y esa variable es la única que
gana sobre el archivo, porque `dj_database_url.config()` lee `os.environ` primero y usa
el valor de decouple solo como fallback.

## 5. Migrar y arrancar

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La app queda en http://127.0.0.1:8000/ y entra por `/login/`.

## 6. Comandos habituales

```bash
# Pruebas de muestreo (39, todas deben pasar)
python manage.py test core.sampling -v 2

# Toda la suite
python manage.py test

# Ver qué muestras se crearían hoy, sin escribir en la base
python manage.py generate_samplings --dry-run

# Crearlas
python manage.py generate_samplings
```

El `scheduler-luka` ya corre ese mismo comando cada hora contra tu base local; puedes
verlo con `docker compose logs -f scheduler-luka`. Invocarlo a mano no molesta: es
idempotente.

## Problemas frecuentes

**`error: metadata-generation-failed` al instalar pycairo** — falta `pkg-config`.
`brew install pkg-config` y reinstala. Comprueba con `pkg-config --modversion cairo`.

**`KeyError: 'AWS_ACCESS_KEY_ID'`** (o cualquier otra variable) — esa clave está vacía
en tu `.env`. Ponle un valor de relleno.

**`ImproperlyConfigured: settings.DATABASES is improperly configured`** — falta
`DATABASE_URL`, o decouple no encontró el `.env`. Confirma que está en `luka/.env`.

**`connection refused` al puerto 5432** — la base no está arriba (`docker compose up -d`)
o el puerto está ocupado por otro PostgreSQL. Comprueba quién lo tiene con
`lsof -nP -iTCP:5432 -sTCP:LISTEN`; si es un `postgresql` de brew, párala con
`brew services stop postgresql@16`.

**El `scheduler-luka` reinicia en bucle con `Failed to fork exec`** — el `command:` del
compose debe usar la ruta absoluta `/usr/local/bin/supercronic`. Como PID 1, supercronic
activa el reaper, que se re-ejecuta con `ForkExec(os.Args[0])` sin resolver el `PATH`, y
con el nombre pelado no se encuentra a sí mismo.

**La app arranca pero cambias `luka/.env` y no pasa nada** — decouple lee el archivo al
importar los settings; reinicia el `runserver`.
