"""Modelo base abstracto para todos los modelos del sistema.

Proporciona campos de auditoría (usuario y fecha de creación/actualización)
que son heredados por todas las tablas del sistema Luka LIS.
"""

from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """Modelo abstracto que agrega trazabilidad de auditoría a todas las tablas.

    Provee los campos ``user_creation``, ``date_creation``, ``user_updated``
    y ``date_updated`` para registrar quién y cuándo creó o modificó cada
    registro.
    """
    user_creation = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='%(app_label)s_%(class)s_creation', null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user_updated = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name='%(app_label)s_%(class)s_updated',  null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        """Configuración del modelo base abstracto."""
        abstract = True
