import uuid

from crum import get_current_user
from django.db import models, transaction

from core.laboratory.models import Laboratory
from core.models import BaseModel
from core.user.models import User


# Equipos Instrumentales
class EquipmentInstrumental(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    code_equipment = models.CharField(max_length=20, verbose_name='Código')
    description_equipment = models.CharField(max_length=200, verbose_name='Descripción')
    supplier_equipment = models.CharField(max_length=200, verbose_name='Proveedor')
    brand_equipment = models.CharField(max_length=100, verbose_name='Marca')
    model_equipment = models.CharField(max_length=50, verbose_name='Modelo')
    serie_equipment = models.CharField(max_length=20, verbose_name='Serie')
    laboratory = models.ForeignKey(Laboratory, verbose_name='Ubicación', on_delete=models.CASCADE)
    date_start_use = models.DateField(verbose_name='Fecha de Inicio Uso', null=True, blank=True)
    date_disabled = models.DateField(verbose_name='Fecha de Inactivación', null=True, blank=True)
    time_use = models.FloatField(verbose_name='Tiempo de Uso (Horas)', null=True, blank=True)
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    photo_equipment = models.FileField(upload_to='equipment/instrumental/%Y%m%d', verbose_name='Foto del Equipo', null=True, blank=True)
    manual_equipment = models.FileField(upload_to='equipment/instrumental/%Y%m%d', verbose_name='Manual de Operación', null=True, blank=True)
    enable_equipment = models.BooleanField(default=True, verbose_name='Habilitado')
    frequency_calibration = models.FloatField(verbose_name='Frecuencia de Calibración (Meses)', default=12)
    frequency_maintenance = models.PositiveSmallIntegerField(verbose_name='Frecuencia de Mantenimiento (Meses)', default=12)
    intermediate_verification = models.PositiveSmallIntegerField(verbose_name='Verificación Intermedia (Meses)', default=1)
    tolerance = models.FloatField(verbose_name='Error Máximo Permitido', null=True, blank=True)
    unit_tolerance = models.CharField(verbose_name='Unidad de Medida', max_length=10, null=True, blank=True)
    date_calibration_fix = models.DateField(verbose_name='Fecha de Calibración Inicial', null=True, blank=True)

    def __str__(self):
        return f'{self.code_equipment} - {self.description_equipment}, {self.brand_equipment} - {self.model_equipment}'

    class Meta:
        verbose_name = 'EquipmentInstrumental'
        verbose_name_plural = 'EquipmentInstrumentals'
        db_table = 'EquipmentInstrumental'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(EquipmentInstrumental, self).save(*args, **kwargs)


# Generador de códigos de material instrumental
def code_instrumental_generator():
    """
    Genera el siguiente código secuencial de forma segura bloqueando la fila.
    Inicia en 2000001 y aumenta de 1 en 1.
    """
    last_material = MaterialInstrumental.objects.select_for_update().filter(code_instrumental__regex=r'^\d+$').order_by('-code_instrumental').first()

    if not last_material:
        return "2000001"

    current_number = int(last_material.code_instrumental)
    new_number = current_number + 1
    return str(new_number)


# Material Instrumental o de Laboratorio
class MaterialInstrumental(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    code_instrumental = models.CharField(max_length=20, verbose_name='Código', unique=True, blank=True)
    description_instrumental = models.CharField(max_length=200, verbose_name='Descripción')
    supplier_equipment = models.CharField(max_length=200, verbose_name='Proveedor')
    brand_instrumental = models.CharField(max_length=100, verbose_name='Marca')
    date_disabled = models.DateField(verbose_name='Fecha de Inactivación', null=True, blank=True)
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    photo_instrumental = models.FileField(
        upload_to='equipment/material/%Y%m%d', verbose_name='Foto del Material', null=True, blank=True)
    enable_instrumental = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return f'{self.code_instrumental} - {self.description_instrumental}, {self.brand_instrumental}'

    class Meta:
        verbose_name = 'MaterialInstrumental'
        verbose_name_plural = 'MaterialInstrumentals'
        db_table = 'MaterialInstrumental'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user

        # Automatización del código con protección de concurrencia
        if not self.code_instrumental:
            # Envolvemos en una transacción atómica para que el select_for_update funcione
            with transaction.atomic(using=kwargs.get('using')):
                self.code_instrumental = code_instrumental_generator()
                return super(MaterialInstrumental, self).save(*args, **kwargs)

        return super(MaterialInstrumental, self).save(*args, **kwargs)


# Mantenimiento
class Maintenance(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)
    date_maintenance = models.DateField(verbose_name='Fecha')
    next_date_maintenance = models.DateField(verbose_name='Fecha Próximo Mantenimiento:')
    type_maintenance = models.CharField(max_length=50, verbose_name='Tipo de Mantenimiento')
    maintenance_by = models.CharField(max_length=250, verbose_name='Realizado por')
    description_maintenance = models.TextField(verbose_name='Descripción del Mantenimiento')
    parts_change_maintenance = models.TextField(verbose_name='Partes o Piezas Reemplazadas')
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    file_maintenance = models.FileField(upload_to='maintenance/%Y%m%d', verbose_name='Registro Físico de Mantenimiento', null=True, blank=True)
    maintenance_next_completed = models.BooleanField(verbose_name='Próximo Mtto Completado', default=False)

    def __str__(self):
        return f'{self.equipment_instrumental} - {self.date_maintenance} - {self.type_maintenance}'

    class Meta:
        verbose_name = 'Maintenance'
        verbose_name_plural = 'Maintenances'
        db_table = 'Maintenance'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Maintenance, self).save(*args, **kwargs)


# Calibración
class Calibration(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)
    date_calibration = models.DateField(verbose_name='Fecha')
    date_calibration_next = models.DateField(verbose_name='Próxima Calibración')
    calibrated_by = models.CharField(max_length=250, verbose_name='Calibrado por')
    parameter = models.CharField(max_length=250, verbose_name='Parametro', null=True, blank=True)
    observation_calibration = models.TextField(verbose_name='Observaciones', default='No aplica')
    comply = models.BooleanField(verbose_name='Cumple')
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    certificate_calibration = models.FileField(upload_to='calibration/%Y%m%d', verbose_name='Certificado de Calibración', null=True, blank=True)
    calibration_next_completed = models.BooleanField(verbose_name='Próxima Calibración completada', default=False)

    def __str__(self):
        return f'{self.equipment_instrumental} - {self.date_calibration} - Calibración: {"Cumple" if self.comply else "No cumple"}'

    class Meta:
        verbose_name = 'Calibration'
        verbose_name_plural = 'Calibrations'
        db_table = 'Calibration'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Calibration, self).save(*args, **kwargs)


# Verificaciones Intermedias
class Verification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)
    date_verification = models.DateField(verbose_name='Fecha')
    date_verification_next = models.DateField(verbose_name='Próxima Verificación')
    verified_by = models.CharField(max_length=250, verbose_name='Verificado por')
    parameter_verified = models.CharField(max_length=250, verbose_name='Parametro', null=True, blank=True)
    reference_pattern = models.FileField(upload_to='verification/reference_patterns/%Y%m%d', verbose_name='Patrón de Referencia', null=True, blank=True)
    observation_verification = models.TextField(verbose_name='Observaciones', default='No aplica')
    comply = models.BooleanField(verbose_name='Cumple')
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    report_verification = models.FileField(upload_to='verification/%Y%m%d', verbose_name='Reporte de Verificación', null=True, blank=True)

    def __str__(self):
        return f'{self.equipment_instrumental} - {self.date_verification} - Verificación: {"Cumple" if self.comply else "No cumple"}'

    class Meta:
        verbose_name = 'Verification'
        verbose_name_plural = 'Verifications'
        db_table = 'Verification'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Verification, self).save(*args, **kwargs)


# Patrones de Referencia
class ReferencePattern(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Instrumento', on_delete=models.CASCADE)
    description_pattern = models.CharField(max_length=150, verbose_name='Descripción del Patrón', null=True, blank=True)
    magnitude_pattern = models.FloatField(verbose_name='Magnitud del Patrón', null=True, blank=True)
    unit_pattern = models.CharField(verbose_name='Unidad del Patrón', max_length=50, null=True, blank=True)
    date_expire_calibration = models.DateField(verbose_name='Fecha de Expiración', null=True, blank=True)
    certificate_calibration = models.FileField(verbose_name='Certificado de Calibración', upload_to='calibration_certificates_pattern/', null=True, blank=True)

    def __str__(self):
        return f'{self.description_pattern} - {self.magnitude_pattern} {self.unit_pattern}'

    class Meta:
        verbose_name = 'ReferencePattern'
        verbose_name_plural = 'ReferencePatterns'
        db_table = 'ReferencePattern'

    def toJSON(self):
        item = {
            'id': str(self.id),
            'equipment_instrumental': self.equipment_instrumental.toJSON() if hasattr(self.equipment_instrumental, 'toJSON') else str(self.equipment_instrumental),
            'description_pattern': self.description_pattern,
            'magnitude_pattern': self.magnitude_pattern,
            'unit_pattern': self.unit_pattern,
            'date_expire_calibration': self.date_expire_calibration.strftime('%Y-%m-%d') if self.date_expire_calibration else None,
            'certificate_calibration': self.certificate_calibration.url if self.certificate_calibration else None,
        }
        return item

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(ReferencePattern, self).save(*args, **kwargs)


# Verificación Diaria
class DailyVerification(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)
    date_verification_daily = models.DateTimeField(verbose_name='Fecha y Hora')
    parameter_verified = models.CharField(max_length=250, verbose_name='Parametro')
    reference_pattern = models.ForeignKey(ReferencePattern, verbose_name='Patrón de Referencia', on_delete=models.CASCADE)
    verification_result_daily = models.FloatField(verbose_name='Resultado')
    error = models.FloatField(verbose_name='Error')
    observation_verification = models.TextField(verbose_name='Observaciones', default='No aplica')
    comply = models.BooleanField(verbose_name='Cumple')
    verified_by = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.equipment_instrumental} - {self.date_verification_daily} - Verificación: {"Cumple" if self.comply else "No cumple"}'

    class Meta:
        verbose_name = 'DailyVerification'
        verbose_name_plural = 'DailyVerifications'
        db_table = 'DailyVerification'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(DailyVerification, self).save(*args, **kwargs)
