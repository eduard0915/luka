# Correr el proyecto en local sin Docker

Guía verificada en macOS (Apple Silicon) contra este repo. Para correrlo con Docker
ver `docs/deploy/scheduler.md` y el `docker-compose.yml`.

## 1. Dependencias del sistema

```bash
brew install python@3.13 postgresql@16 cairo pkg-config
```

`pkg-config` no es opcional: sin él la instalación de `pycairo` falla con
`error: metadata-generation-failed` porque no encuentra las cabeceras de cairo. Es el
error más común al montar este proyecto desde cero.

Sobre la versión de Python: la imagen de Docker usa 3.12, pero el proyecto corre bien
en 3.13 (verificado: las 39 pruebas de `core.sampling` pasan). Evita 3.14 por ahora —
varias dependencias compiladas aún no publican wheels para esa versión.

## 2. Levantar PostgreSQL

```bash
brew services start postgresql@16
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"   # añádelo a tu ~/.zshrc
```

Crear el rol y la base. El rol necesita `CREATEDB` porque el runner de pruebas crea y
destruye una base `test_luka` en cada corrida:

```bash
psql -d postgres -c "CREATE ROLE luka LOGIN PASSWORD 'luka' CREATEDB"
createdb -O luka luka
```

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

| Archivo | Para qué | Host de la BD |
|---------|----------|---------------|
| `luka/.env` | desarrollo local sin Docker | `localhost` |
| `.env` (raíz) | interpolar `${VARIABLES}` en `docker-compose.yml` | `db-luka` |

decouple busca desde `luka/settings.py` hacia arriba, así que encuentra `luka/.env`
primero y la raíz solo si aquel no existe. Manteniéndolos separados, correr en local y
con Docker no se pisan. Ambos están en el `.gitignore`, y el `.dockerignore` impide que
cualquiera de los dos entre en la imagen (si entrara, sobrescribiría en silencio el
`SECRET_KEY` y el `DEBUG` del despliegue).

Excepción útil: `DATABASE_URL` es la única que sí respeta la variable de entorno por
encima del archivo, porque `dj_database_url.config()` lee `os.environ` primero y usa el
valor de decouple solo como fallback.

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

En local no hace falta el cron: el scheduler es el contenedor `scheduler-luka` del
despliegue. Para probar la generación basta con invocar el comando a mano.

## Problemas frecuentes

**`error: metadata-generation-failed` al instalar pycairo** — falta `pkg-config`.
`brew install pkg-config` y reinstala. Comprueba con `pkg-config --modversion cairo`.

**`KeyError: 'AWS_ACCESS_KEY_ID'`** (o cualquier otra variable) — esa clave está vacía
en tu `.env`. Ponle un valor de relleno.

**`ImproperlyConfigured: settings.DATABASES is improperly configured`** — falta
`DATABASE_URL`, o decouple no encontró el `.env`. Confirma que está en `luka/.env`.

**`connection refused` al puerto 5432** — PostgreSQL no está corriendo:
`brew services start postgresql@16`. Verifica con `pg_isready`.

**`permission denied to create database` al correr las pruebas** — al rol `luka` le
falta `CREATEDB`: `psql -d postgres -c "ALTER ROLE luka CREATEDB"`.

**La app arranca pero cambias `luka/.env` y no pasa nada** — decouple lee el archivo al
importar los settings; reinicia el `runserver`.
