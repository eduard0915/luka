# Luka

Sistema de gestión de laboratorio (LIMS): productos y puntos de muestreo, métodos
analíticos, muestreos y sus análisis, soluciones y reactivos, equipos y condiciones
ambientales.

Django 6.0 · PostgreSQL 16 · Python 3.12 (Docker) / 3.13 (local)

## Arrancar

El servidor corre en tu máquina y sus dependencias (base de datos y cron) en Docker:

```bash
cp .env.example .env                    # para docker compose
docker compose up -d                    # base en 127.0.0.1:5432 + scheduler

python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt         # necesita: brew install cairo pkg-config
# crea luka/.env (ver la guía)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La app queda en http://127.0.0.1:8000/ y entra por `/login/`.

Guía completa, con los errores típicos y su causa →
[`docs/desarrollo-local.md`](docs/desarrollo-local.md)

## Los dos compose

| Archivo | Para qué |
|---------|----------|
| `docker-compose.yml` | dependencias de desarrollo local: base (con puerto publicado) y scheduler |
| `docker-compose.dokploy.yml` | stack completo de producción; es el que despliega Dokploy |

Son archivos independientes a propósito, no un override: el merge de compose solo suma,
así que no habría forma de quitarle el puerto publicado al de producción. Si tocas un
servicio, revisa si el cambio aplica también al otro.

## Configuración

Las variables se leen con `django-decouple`, que tiene dos comportamientos que
conviene conocer antes de perder una tarde:

- **El archivo `.env` gana sobre las variables de entorno** (al revés de lo habitual).
- **Un valor vacío no es "vacío"**: cae a la variable de entorno y, si no existe,
  revienta con `KeyError` al arrancar. Usa un valor de relleno.

De ahí la convención de dos archivos, ninguno versionado:

| Archivo | Para qué | Host de la BD |
|---------|----------|---------------|
| `luka/.env` | desarrollo local sin Docker | `localhost` |
| `.env` (raíz) | interpolar `${VARIABLES}` en `docker-compose.yml` | `db-luka` |

`.env.example` es la plantilla. El `.dockerignore` impide que cualquier `.env` entre en
la imagen: si entrara, sobrescribiría en silencio el `SECRET_KEY` y el `DEBUG` del
despliegue.

## Pruebas

```bash
python manage.py test                 # toda la suite
python manage.py test core.sampling   # solo muestreo (39 pruebas)
```

## Muestreo automático

Cada hora se generan las muestras programadas del día para cada grupo de muestreo
habilitado, con recuperación de días perdidos e idempotencia. Lo dispara el servicio
`scheduler-luka` del compose.

```bash
python manage.py generate_samplings --dry-run   # qué se crearía, sin escribir
python manage.py generate_samplings             # crearlas
```

Operación y despliegue → [`docs/deploy/scheduler.md`](docs/deploy/scheduler.md)
Diseño y decisiones → [`docs/superpowers/specs/`](docs/superpowers/specs/)

## Estructura

```
core/            apps del dominio
  analytical_method/  métodos analíticos y sus cálculos
  company/            empresa, plantas y procesos
  condition/          condiciones ambientales
  equipment/          equipos, calibraciones y mantenimientos
  laboratory/         laboratorios
  observation/        observaciones
  product/            productos, especificaciones y puntos de muestreo
  reagent/            reactivos
  report/             reportes
  sampling/           grupos de muestreo, muestras y análisis
  solution/           soluciones estándar
  user/               usuarios y capacitaciones
  home/ login/ start/ vistas de entrada y navegación
luka/            settings, urls y wsgi
templates/       plantillas base
static/          css, js e imágenes
docs/            documentación
```
