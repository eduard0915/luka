import uuid

from crum import get_current_user
from django.db import models, transaction
from django.utils import timezone

from core.models import BaseModel
from core.product.models import SamplePoint
from core.user.models import User


# Generador de Número de Muestra
def code_sample_generator():
    today = timezone.localdate()
    today_str = today.strftime('%Y%m%d')

    # Buscar el último registro del día actual
    with transaction.atomic():
        last_sample = SamplingProcess.objects.filter(
            date_creation__date=today
        ).select_for_update().order_by('-date_creation').first()

        sufix_sample = last_sample.group_sampling.sampling_point.sample_point_code

        if not last_sample:
            # Primer registro del día
            return f'{sufix_sample}-{today_str}-1'

        # Extraer el número secuencial del código existente
        code_parts = last_sample.number_sample.split('-')
        current_number = int(code_parts[1])
        new_number = current_number + 1

        return f'{sufix_sample}-{today_str}-{new_number}'


# Grupos de Muestreo
class SamplingGroup(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_point = models.ForeignKey(SamplePoint, verbose_name='Punto de Muestreo', on_delete=models.CASCADE)
    hour_sampling = models.TimeField(verbose_name='Hora del Primer Muestreo', default='07:00:00')
    number_sampling_day = models.PositiveSmallIntegerField(verbose_name='Muestras por Día')
    enable_sampling_group = models.BooleanField(verbose_name='Habilitado', default=True)

    def __str__(self):
        return str(self.sampling_point)

    class Meta:
        verbose_name = 'SamplingGroup'
        verbose_name_plural = 'SamplingGroups'
        db_table = 'SamplingGroup'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingGroup, self).save(*args, **kwargs)


# Grupos de Muestreo
class SamplingProcess(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    group_sampling = models.ForeignKey(SamplingGroup, verbose_name='Grupo de Muestreo', on_delete=models.CASCADE)
    date_sampling_scheduled = models.DateTimeField(verbose_name='Programación de Muestreo')
    date_sampling = models.DateTimeField(verbose_name='Fecha y Hora de Muestreo')
    number_sample = models.CharField(verbose_name='N° de Muestra', max_length=25, default=code_sample_generator)
    automatic_sampling = models.BooleanField(verbose_name='Muestreo Automático', default=True)
    sampling_confirmed_by = models.ForeignKey(User, verbose_name='Confirmado por', on_delete=models.CASCADE, related_name='sampling_confirmed_by', null=True, blank=True)
    sampling_created_by = models.ForeignKey(User, verbose_name='Realizado por', on_delete=models.CASCADE, related_name='sampling_created_by', null=True, blank=True)
    status_sampling = models.CharField(verbose_name='Estado de la Muestra', max_length=20, default='Programada')
    image_sample = models.FileField(upload_to='sampling/%Y%m%d', verbose_name='Foto de la Muestra', null=True, blank=True)
    batch_number = models.CharField(verbose_name='N° de Lote', max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.number_sample)

    class Meta:
        verbose_name = 'SamplingProcess'
        verbose_name_plural = 'SamplingsProcess'
        db_table = 'SamplingProcess'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingProcess, self).save(*args, **kwargs)
