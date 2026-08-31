"""Punto de entrada WSGI para el proyecto Luka LIS.

Expone la aplicación WSGI como una variable de nivel de módulo
llamada ``application``.

Para más información, consulte:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luka.settings')

application = get_wsgi_application()
