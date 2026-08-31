"""Modelos de la aplicación de observaciones.

Define la entidad Observation para almacenar comentarios asociados
a procesos de muestreo.
"""  # noqa: E501

import uuid

from crum import get_current_user
from django.db import models

from core.models import BaseModel
from core.sampling.models import SamplingProcess
from core.user.models import User


class Observation(BaseModel):
    """Comentario u observación asociada a un proceso de muestreo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comment = models.TextField(verbose_name='Comentario')
    comment_by = models.ForeignKey(User, verbose_name='Comentado por', on_delete=models.CASCADE)
    comment_date = models.DateTimeField(verbose_name='Fecha de Comentario', auto_now_add=True)
    sampling_process = models.ForeignKey(SamplingProcess, verbose_name='Muestra', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Devuelve el contenido del comentario como representación legible."""
        return str(self.comment)

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        db_table = 'Observation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Asigna el usuario de creación o actualización antes de guardar."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Observation, self).save(*args, **kwargs)
