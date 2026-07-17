# Luka

Sistema de gestión de laboratorio (LIMS): productos y puntos de muestreo, métodos
analíticos, muestreos y sus análisis, soluciones y reactivos, equipos y condiciones
ambientales.

Django 6.0 · PostgreSQL 16 · Python 3.12 (Docker) / 3.13 (local)

## Arrancar

**En local, sin Docker** → [`docs/desarrollo-local.md`](docs/desarrollo-local.md)
Guía paso a paso verificada: dependencias del sistema, PostgreSQL, entorno virtual,
variables de entorno y los errores típicos con su causa.

**Con Docker:**

```bash
cp .env.example .env          # ajusta DATABASE_URL a @db-luka:5432
docker compose up -d --build
docker compose exec web-luka python manage.py migrate
docker compose exec web-luka python manage.py createsuperuser
```

La app queda en http://127.0.0.1:8000/ y entra por `/login/`.

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
python manage.py test                    # local
docker compose run --rm web-luka python manage.py test    # en Docker
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
