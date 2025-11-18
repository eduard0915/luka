import uuid

from crum import get_current_user
from django.db import models

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


# Material Instrumental o de Laboratorio
class MaterialInstrumental(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    code_instrumental = models.CharField(max_length=20, verbose_name='Código')
    description_instrumental = models.CharField(max_length=200, verbose_name='Descripción')
    supplier_equipment = models.CharField(max_length=200, verbose_name='Proveedor')
    brand_instrumental = models.CharField(max_length=100, verbose_name='Marca')
    date_disabled = models.DateField(verbose_name='Fecha de Inactivación', null=True, blank=True)
    responsible_user = models.ForeignKey(User, verbose_name='Responsable', on_delete=models.CASCADE)
    photo_instrumental = models.FileField(upload_to='equipment/material/%Y%m%d', verbose_name='Foto del Equipo', null=True, blank=True)
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
        return super(MaterialInstrumental, self).save(*args, **kwargs)
