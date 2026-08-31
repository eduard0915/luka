"""Punto de entrada ASGI para el proyecto Luka LIS.

Expone la aplicación ASGI como una variable de nivel de módulo
llamada ``application``.

Para más información, consulte:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luka.settings')

application = get_asgi_application()
