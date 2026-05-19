import uuid

from crum import get_current_user
from django.db import models

from core.models import BaseModel
from core.sampling.models import SamplingProcess
from core.user.models import User


# Observaciones varias
class Observation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comment = models.TextField(verbose_name='Comentario')
    comment_by = models.ForeignKey(User, verbose_name='Comentado por', on_delete=models.CASCADE)
    comment_date = models.DateTimeField(verbose_name='Fecha de Comentario', auto_now_add=True)
    sampling_process = models.ForeignKey(SamplingProcess, verbose_name='Muestra', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.comment)

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        db_table = 'Observation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Observation, self).save(*args, **kwargs)
