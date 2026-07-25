"""Modelos de la aplicación de laboratorios.

Define la entidad Laboratory que representa un laboratorio asociado a una planta.
"""  # noqa: E501

import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Site


class Laboratory(models.Model):
    """Representa un laboratorio asociado a una planta (site) dentro del sistema."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    laboratory_name = models.CharField(max_length=120, verbose_name='Descripción del Laboratorio')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Planta')
    enable_laboratory = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        """Devuelve el nombre del laboratorio como representación legible."""
        return f'{self.laboratory_name} - {self.site}'
    class Meta:
        verbose_name = 'Laboratory'
        verbose_name_plural = 'Laboratories'
        db_table = 'Laboratory'


def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
    """Asigna el usuario de creación o actualización antes de guardar."""
    user = get_current_user()
    if user:
        if not self.user_creation:
            self.user_creation = user
        else:
            self.user_updated = user
    return super(Laboratory, self).save(*args, **kwargs)
