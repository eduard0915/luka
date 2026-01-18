import uuid

from crum import get_current_user
from django.db import models, transaction
from django.utils import timezone

from core.analytical_method.models import AnalyticalMethod
from core.models import BaseModel
from core.product.models import SamplePoint
from core.solution.models import SolutionStd
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
    first_hour_sampling = models.TimeField(verbose_name='Hora del Primer Muestreo', default='07:00:00')
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


# Muestreo
class SamplingProcess(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    group_sampling = models.ForeignKey(SamplingGroup, verbose_name='Grupo de Muestreo', on_delete=models.CASCADE, null=True, blank=True)
    point_sampling = models.ForeignKey(SamplePoint, verbose_name='Punto de Muestreo', on_delete=models.CASCADE, null=True, blank=True)
    type_sampling = models.CharField(verbose_name='Tipo de Muestreo', max_length=30)
    date_sampling_scheduled = models.DateTimeField(verbose_name='Programación de Muestreo')
    date_sampling = models.DateTimeField(verbose_name='Fecha y Hora de Muestreo', null=True, blank=True)
    number_sample = models.CharField(verbose_name='N° de Muestra', max_length=25)
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

        if not self.number_sample:
            self.number_sample = self.generate_sample_code()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingProcess, self).save(*args, **kwargs)

    def generate_sample_code(self):
        today = timezone.localdate()
        today_str = today.strftime('%Y%m%d')

        # Obtener el código del punto de muestreo
        if self.group_sampling:
            sufix_sample = self.group_sampling.sampling_point.sample_point_code
            sampling_point = self.group_sampling.sampling_point
        elif self.point_sampling:
            sufix_sample = self.point_sampling.sample_point_code
            sampling_point = self.point_sampling
        else:
            raise ValueError("Debe especificar Grupo de Muestreo o Punto de Muestreo para generar el código de la muestra")

        with transaction.atomic():
            # Buscar el último registro del día para el mismo punto de muestreo
            last_sample = SamplingProcess.objects.filter(
                date_creation__date=today
            ).select_for_update().order_by('-date_creation').first()

            # Filtrar por punto de muestreo según el caso
            if last_sample:
                # Verificar que sea del mismo punto de muestreo
                last_sample_point = None
                if last_sample.group_sampling:
                    last_sample_point = last_sample.group_sampling.sampling_point
                elif last_sample.sampling_point:
                    last_sample_point = last_sample.sampling_point

                # Si no es del mismo punto o no hay muestra previa, empezar desde 1
                if not last_sample_point or last_sample_point.id != sampling_point.id:
                    return f'{sufix_sample}-{today_str}-1'

                # Extraer el número secuencial del código existente
                code_parts = last_sample.number_sample.split('-')
                current_number = int(code_parts[-1])
                new_number = current_number + 1

                return f'{sufix_sample}-{today_str}-{new_number}'
            else:
                # Primer registro del día
                return f'{sufix_sample}-{today_str}-1'


# Análisis de la Muestra
class SamplingAnalysis(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_process = models.ForeignKey(SamplingProcess, verbose_name='Muestra', on_delete=models.CASCADE)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    average_concentration = models.FloatField(verbose_name='Resultado', null=True, blank=True)
    standard_deviation = models.FloatField(verbose_name='Desviación Estándar', null=True, blank=True)
    coefficient_variation = models.FloatField(verbose_name='Coeficiente de Variación', null=True, blank=True)
    comply = models.CharField(max_length=10, verbose_name='Concepto', null=True, blank=True)

    def __str__(self):
        return str(self.sampling_process)

    class Meta:
        verbose_name = 'SamplingAnalysis'
        verbose_name_plural = 'SamplingsAnalysis'
        db_table = 'SamplingAnalysis'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingAnalysis, self).save(*args, **kwargs)


# Procesamiento de la muestra
class SamplingAnalysisProcessing(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sample_analysis = models.ForeignKey(SamplingAnalysis, verbose_name='Análisis de la Muestra', on_delete=models.CASCADE)
    standard_solution = models.ForeignKey(SolutionStd, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    quantity_standard = models.FloatField(verbose_name=' Cantidad de Estándar')
    quantity_solution = models.FloatField(verbose_name='mL de Solución Muestra Gastados')
    concentration_sln = models.FloatField(verbose_name='Concentración Sln')
    analyzed_by = models.ForeignKey(User, verbose_name='Analizado por', on_delete=models.CASCADE)
    analyzed_date = models.DateField(verbose_name='Fecha de Análisis')

    def __str__(self):
        return str(self.quantity_standard)

    class Meta:
        verbose_name = 'SamplingAnalysisProcessing'
        verbose_name_plural = 'SamplingAnalysisProcessing'
        db_table = 'SamplingAnalysisProcessing'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingAnalysisProcessing, self).save(*args, **kwargs)
