import os
from pathlib import Path

import dj_database_url
from decouple import config

from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG')

ALLOWED_HOSTS = ['127.0.0.1', '.herokuapp.com', 'localhost', '.run.app']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps
    'core.user',
    'core.start',
    'core.login',
    'core.home',
    'core.company',
    'core.reagent',
    # Libs
    'widget_tweaks',
    'django_password_history',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'luka.urls'

INTERNAL_IPS = ["127.0.0.1", 'localhost']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.extras_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'luka.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'dev': dj_database_url.config(
        default=config('DATABASE_TEST')
    ),
    'production': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

DATABASES['default'] = DATABASES['dev' if DEBUG else 'production']

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-col'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

AUTH_USER_MODEL = 'user.User'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOGIN_REDIRECT_URL = '/start/'

LOGOUT_REDIRECT_URL = '/login/'

LOGIN_URL = '/login/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'
# MEDIA_URL = config('MEDIA_URL')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

TIME_PASSWORD_EXPIRE = 90

# access with url from cloud run service
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000/',
    'http://localhost:8000/',
    'https://*.lukalims.com',
    'https://*.herokuapp.com',
    'https://*.run.app',
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://*.lukalims.com',
]

# Conexión AWS S3
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('BUCKET')
REGION_NAME = config('REGION_NAME')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'config.storages.MediaStore'

# Configuración de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas en segundos
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'django_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
