"""Modelos de datos para la aplicación de muestreo del laboratorio."""

import uuid

from crum import get_current_user
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.forms import model_to_dict
from django.utils import timezone

from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculateRelation, HeavyMetal
from core.models import BaseModel
from core.product.models import SamplePoint
from core.solution.models import SolutionStd
from core.user.models import User


class SamplingGroup(BaseModel):
    """Modelo que representa un grupo de muestreo asociado a un punto de muestreo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_point = models.ForeignKey(SamplePoint, verbose_name='Punto de Muestreo', on_delete=models.CASCADE)
    first_hour_sampling = models.TimeField(verbose_name='Hora del Primer Muestreo', default='07:00:00')
    number_sampling_day = models.PositiveSmallIntegerField(verbose_name='Muestras por Día', validators=[MinValueValidator(1)])
    enable_sampling_group = models.BooleanField(verbose_name='Habilitado', default=True)
    enable_sampling_auto = models.BooleanField(verbose_name='Automuestreo Habilitado', default=True)

    def __str__(self):
        """Devuelve el punto de muestreo como representación del grupo."""
        return str(self.sampling_point)

    class Meta:
        verbose_name = 'SamplingGroup'
        verbose_name_plural = 'SamplingGroups'
        db_table = 'SamplingGroup'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el grupo asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingGroup, self).save(*args, **kwargs)


class SamplingProcess(BaseModel):
    """Modelo que representa un proceso de muestreo individual."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    group_sampling = models.ForeignKey(SamplingGroup, verbose_name='Grupo de Muestreo', on_delete=models.CASCADE, null=True, blank=True)
    point_sampling = models.ForeignKey(SamplePoint, verbose_name='Punto de Muestreo', on_delete=models.CASCADE, null=True, blank=True)
    type_sampling = models.CharField(verbose_name='Tipo de Muestreo', max_length=30)
    date_sampling_scheduled = models.DateTimeField(verbose_name='Programación de Muestreo')
    date_sampling = models.DateTimeField(verbose_name='Fecha y Hora de Muestreo', null=True, blank=True)
    number_sample = models.CharField(verbose_name='N° de Muestra', max_length=45, db_index=True)
    automatic_sampling = models.BooleanField(verbose_name='Muestreo Automático', default=True)
    sampling_confirmed_by = models.ForeignKey(User, verbose_name='Confirmado por', on_delete=models.CASCADE, related_name='sampling_confirmed_by', null=True, blank=True)
    sampling_created_by = models.ForeignKey(User, verbose_name='Realizado por', on_delete=models.CASCADE, related_name='sampling_created_by', null=True, blank=True)
    status_sampling = models.CharField(verbose_name='Estado de la Muestra', max_length=20, default='Programada')
    image_sample = models.FileField(upload_to='sampling/%Y%m%d', verbose_name='Foto de la Muestra', null=True, blank=True)
    batch_number = models.CharField(verbose_name='N° de Lote', max_length=20, blank=True, null=True)
    approved_by = models.ForeignKey(User, verbose_name='Aprobado por', on_delete=models.CASCADE, related_name='approved_by', null=True, blank=True)
    date_approved = models.DateTimeField(verbose_name='Fecha de Aprobado', null=True, blank=True)
    approved = models.BooleanField(verbose_name='Aprobado', default=False)

    def __str__(self):
        """Devuelve el número de muestra como representación del proceso."""
        return str(self.number_sample)

    def toJSON(self):
        """Serializa el proceso de muestreo a un diccionario JSON."""
        item = model_to_dict(self, exclude=['image_sample'])
        item['sampling_point'] = self.group_sampling.sampling_point.sample_point_name if self.group_sampling else self.point_sampling.sample_point_name
        item['date_sampling_scheduled'] = timezone.localtime(self.date_sampling_scheduled).strftime('%Y-%m-%d %H:%M:%S')
        item['date_sampling'] = timezone.localtime(self.date_sampling).strftime('%Y-%m-%d %H:%M:%S') if self.date_sampling else ''
        return item

    class Meta:
        verbose_name_plural = 'SamplingsProcess'
        db_table = 'SamplingProcess'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el proceso generando el código de muestra si no existe."""
        user = get_current_user()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user

        if not self.number_sample:
            with transaction.atomic():
                self.number_sample = self.generate_sample_code()
                return super(SamplingProcess, self).save(*args, **kwargs)
        return super(SamplingProcess, self).save(*args, **kwargs)

    def generate_sample_code(self):
        """Genera el código único de la muestra basado en el punto de muestreo y la fecha."""
        if self.group_sampling:
            sampling_point = self.group_sampling.sampling_point
        elif self.point_sampling:
            sampling_point = self.point_sampling
        else:
            raise ValueError('Debe especificar Grupo de Muestreo o Punto de Muestreo para generar el código de la muestra')
        return next_sample_number(sampling_point, timezone.localdate())


def next_sample_number(sampling_point, code_date):
    """Calcula el siguiente código de muestra para un punto y fecha: {codigo}-{AAAAMMDD}-{n}."""
    list(
        SamplePoint.objects.select_for_update()
        .filter(sample_point_code=sampling_point.sample_point_code)
        .order_by('pk')  # orden estable: evita deadlocks entre escritores
        .values_list('pk', flat=True)
    )
    prefix = f"{sampling_point.sample_point_code}-{code_date.strftime('%Y%m%d')}-"
    existing = SamplingProcess.objects.filter(
        number_sample__startswith=prefix,
    ).values_list('number_sample', flat=True)
    max_sequence = 0
    for number in existing:
        suffix = number[len(prefix):]
        if suffix.isdigit():
            max_sequence = max(max_sequence, int(suffix))
    return f'{prefix}{max_sequence + 1}'


class SamplingGenerationLog(BaseModel):
    """Registro de generación automática de muestras para idempotencia y auditoría."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_group = models.ForeignKey(SamplingGroup, verbose_name='Grupo de Muestreo', on_delete=models.CASCADE)
    target_date = models.DateField(verbose_name='Día Generado')
    samples_created = models.PositiveSmallIntegerField(verbose_name='Muestras Creadas', default=0)
    skipped = models.BooleanField(verbose_name='Omitido', default=False)

    def __str__(self):
        """Devuelve el grupo y la fecha como representación del registro."""
        return f'{self.sampling_group} - {self.target_date}'

    class Meta:
        verbose_name = 'SamplingGenerationLog'
        verbose_name_plural = 'SamplingGenerationLogs'
        db_table = 'SamplingGenerationLog'
        constraints = [
            models.UniqueConstraint(fields=['sampling_group', 'target_date'], name='unique_group_target_date'),
        ]


class SamplingAnalysis(BaseModel):
    """Modelo que representa el análisis de una muestra con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_process = models.ForeignKey(SamplingProcess, verbose_name='Muestra', on_delete=models.CASCADE)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE, blank=True, null=True)
    analytical_method_relation = models.ForeignKey(AnalyticalMethodCalculateRelation, verbose_name='Calculo Relacional', on_delete=models.CASCADE, blank=True, null=True)
    average_concentration = models.FloatField(verbose_name='Resultado', null=True, blank=True)
    standard_deviation = models.FloatField(verbose_name='Desviación Estándar', null=True, blank=True)
    coefficient_variation = models.FloatField(verbose_name='Coeficiente de Variación', null=True, blank=True)
    comply = models.CharField(max_length=10, verbose_name='Concepto', null=True, blank=True)
    date_analysis = models.DateTimeField(verbose_name='Fecha de Análisis', null=True, blank=True)
    verified_by = models.ForeignKey(User, verbose_name='Aprobado por', on_delete=models.CASCADE, related_name='verified_by', null=True, blank=True)
    date_verified= models.DateTimeField(verbose_name='Fecha de Aprobado', null=True, blank=True)

    def __str__(self):
        """Devuelve el proceso de muestreo asociado como representación del análisis."""
        return str(self.sampling_process)

    def toJSON(self):
        """Serializa el análisis de muestra a un diccionario JSON."""
        item = model_to_dict(self)
        item['sampling_process'] = self.sampling_process.toJSON()
        item['analytical_method'] = self.analytical_method.description_analytical_method
        item['average_concentration'] = format(self.average_concentration, '.4f') if self.average_concentration else '0.0000'
        item['date_analysis'] = self.date_analysis.strftime('%Y-%m-%d %H:%M:%S') if self.date_analysis else ''
        return item

    class Meta:
        verbose_name_plural = 'SamplingsAnalysis'
        db_table = 'SamplingAnalysis'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el análisis asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingAnalysis, self).save(*args, **kwargs)


class SamplingAnalysisProcessing(BaseModel):
    """Modelo que representa el procesamiento de un análisis de muestra."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sample_analysis = models.ForeignKey(SamplingAnalysis, verbose_name='Análisis de la Muestra', on_delete=models.CASCADE)
    standard_solution = models.ForeignKey(SolutionStd, verbose_name='Solución Estándar', on_delete=models.CASCADE, null=True, blank=True)
    quantity_standard = models.FloatField(verbose_name='mL Estándar', null=True, blank=True)
    weight_obtained = models.FloatField(verbose_name='Peso Obtenido', null=True, blank=True)
    millimole_reacted = models.FloatField(verbose_name='Milimoles que Reaccionan', null=True, blank=True)
    quantity_sample = models.FloatField(verbose_name='Cant. de Muestra', blank=True, null=True)
    concentration_sample = models.FloatField(verbose_name='Concentración Muestra')
    analyzed_by = models.ForeignKey(User, verbose_name='Analizado por', on_delete=models.CASCADE)
    analyzed_date = models.DateTimeField(verbose_name='Fecha de Análisis')
    relational_calculation = models.BooleanField(default=False)
    analytical_method_calculate = models.ForeignKey(
        'analytical_method.AnalyticalMethodCalculate', on_delete=models.CASCADE, null=True, blank=True)
    analytical_method_calculate_relation = models.ForeignKey(
        'analytical_method.AnalyticalMethodCalculateRelation', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Devuelve la concentración de la muestra como representación del procesamiento."""
        return str(self.concentration_sample)

    class Meta:
        verbose_name = 'SamplingAnalysisProcessing'
        verbose_name_plural = 'SamplingAnalysisProcessing'
        db_table = 'SamplingAnalysisProcessing'

    def toJSON(self):
        """Serializa el procesamiento del análisis a un diccionario JSON."""
        item = model_to_dict(self)
        item['sample_analysis'] = self.sample_analysis.toJSON()
        item['analyzed_by'] = self.analyzed_by.get_full_name()
        item['analyzed_date'] = self.analyzed_date.strftime('%Y-%m-%d %H:%M:%S')
        unit = ""
        if self.analytical_method_calculate:
            unit = self.analytical_method_calculate.unit_measure_calculate
        elif self.analytical_method_calculate_relation:
            unit = self.analytical_method_calculate_relation.unit_measure_calculate
        
        if not unit and self.sample_analysis and self.sample_analysis.analytical_method:
            # 1. Buscar en cálculos directos del método
            calc = self.sample_analysis.analytical_method.analyticalmethodcalculate_set.first()
            if calc:
                unit = calc.unit_measure_calculate
            
            # 2. Si no hay, buscar en relaciones de cálculo (para productos específicos)
            if not unit:
                calc_rel = self.sample_analysis.analytical_method.analyticalmethodcalculaterelation_set.first()
                if calc_rel:
                    unit = calc_rel.unit_measure_calculate
            
            # 3. Si no hay, buscar en cualquier registro de AnalyticalMethodCalculate para este método
            if not unit:
                from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation
                fallback_calc = AnalyticalMethodCalculate.objects.filter(
                    analytical_method=self.sample_analysis.analytical_method
                ).exclude(unit_measure_calculate__isnull=True).exclude(unit_measure_calculate="").first()
                if fallback_calc:
                    unit = fallback_calc.unit_measure_calculate
                else:
                    # 4. Último recurso: buscar en cualquier relación de este método
                    fallback_rel = AnalyticalMethodCalculateRelation.objects.filter(
                        analytical_method=self.sample_analysis.analytical_method
                    ).exclude(unit_measure_calculate__isnull=True).exclude(unit_measure_calculate="").first()
                    if fallback_rel:
                        unit = fallback_rel.unit_measure_calculate

        item['concentration_sample_display'] = f"{format(self.concentration_sample, ' .2f')} {unit or ''}".strip()
        return item

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el procesamiento asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingAnalysisProcessing, self).save(*args, **kwargs)


class SamplingAnalysisProcessingRelation(BaseModel):
    """Modelo que representa el cálculo de parámetros con variables relacionadas."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_analysis = models.ForeignKey(SamplingAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    analytical_method_calculate_relation = models.ForeignKey(AnalyticalMethodCalculateRelation, on_delete=models.CASCADE, null=True, blank=True)
    numerator = models.FloatField(verbose_name='Numerador')
    denominator = models.FloatField(verbose_name='Denominador', null=True, blank=True)
    calcule = models.FloatField(verbose_name='Resultado')
    sampling_process = models.ForeignKey(SamplingProcess, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Devuelve el resultado del cálculo como representación."""
        return str(self.calcule)

    class Meta:
        verbose_name = 'SamplingAnalysisProcessingRelation'
        verbose_name_plural = 'SamplingAnalysisProcessingRelations'
        db_table = 'SamplingAnalysisProcessingRelation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación de procesamiento asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplingAnalysisProcessingRelation, self).save(*args, **kwargs)


class MillimoleReacted(BaseModel):
    """Modelo que registra los milimoles que reaccionaron en una valoración por retroceso."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    standard_solution_add = models.ForeignKey(SolutionStd, on_delete=models.CASCADE, related_name='standard_solution_add', verbose_name='Solución Estandar Adicionada')
    standard_solution_spend = models.ForeignKey(SolutionStd, on_delete=models.CASCADE, related_name='standard_solution_spend', verbose_name='Solución Estandar Gastada')
    sampling_analysis = models.ForeignKey(SamplingAnalysis, on_delete=models.CASCADE)
    milliliter_std_add = models.FloatField(verbose_name='Mililitros Adicionados')
    milliliter_std_spend = models.FloatField(verbose_name='Mililitros Gastados')
    millimole = models.FloatField(verbose_name='Milimoles Reaccionaron')
    quantity_sample = models.FloatField(verbose_name='Cantidad de Muestra (g)')

    def __str__(self):
        """Devuelve el valor de milimoles como representación."""
        return str(self.millimole)

    class Meta:
        verbose_name = 'MillimoleReacted'
        verbose_name_plural = 'MillimolesReacted'
        db_table = 'MillimoleReacted'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el registro de milimoles asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(MillimoleReacted, self).save(*args, **kwargs)


class MassiveSampleAnalysis(BaseModel):
    """Modelo que representa el análisis de una muestra con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sampling_process = models.ForeignKey(SamplingProcess, verbose_name='Muestra', on_delete=models.CASCADE)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE, blank=True, null=True)
    heavy_metal = models.ForeignKey(HeavyMetal, verbose_name='Metal', on_delete=models.CASCADE, blank=True, null=True)
    result = models.FloatField(verbose_name='Resultado', null=True, blank=True)
    standard_deviation = models.FloatField(verbose_name='Desviación Estándar', null=True, blank=True)
    coefficient_variation = models.FloatField(verbose_name='Coeficiente de Variación', null=True, blank=True)
    comply = models.CharField(max_length=10, verbose_name='Concepto', null=True, blank=True)
    date_analysis = models.DateTimeField(verbose_name='Fecha de Análisis', null=True, blank=True, db_index=True)
    analized_by = models.ForeignKey(User, verbose_name='Analizado por', on_delete=models.CASCADE, related_name='analized_by', null=True, blank=True)

    def __str__(self):
        return str(self.result)

    def toJSON(self):
        """Serializa el análisis masivo excluyendo desviación, coeficiente y concepto."""
        item = model_to_dict(self, exclude=['standard_deviation', 'coefficient_variation', 'comply'])
        item['sampling_process'] = self.sampling_process.number_sample
        if self.sampling_process.point_sampling:
            product = self.sampling_process.point_sampling.product
        elif self.sampling_process.group_sampling:
            product = self.sampling_process.group_sampling.sampling_point.product
        else:
            product = None
        item['product'] = product.description_product if product else ''
        item['analytical_method'] = self.analytical_method.description_analytical_method if self.analytical_method else ''
        if self.heavy_metal:
            item['metal'] = self.heavy_metal.metal_description
        elif self.analytical_method:
            item['metal'] = ', '.join(
                m.metal_description for m in self.analytical_method.heavymetal_set.all()
            )
        else:
            item['metal'] = ''
        item['result'] = format(self.result, '.4f') if self.result is not None else ''
        item['date_analysis'] = timezone.localtime(self.date_analysis).strftime('%Y-%m-%d %H:%M:%S') if self.date_analysis else ''
        item['analized_by'] = self.analized_by.get_full_name() if self.analized_by else ''
        return item

    class Meta:
        verbose_name = 'MassiveSampleAnalysis'
        verbose_name_plural = 'MassSampleAnalysis'
        db_table = 'MassiveSampleAnalysis'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el registro de milimoles asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(MassiveSampleAnalysis, self).save(*args, **kwargs)
