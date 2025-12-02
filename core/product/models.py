import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Process
from core.models import BaseModel


# Productos
class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    code_product = models.CharField(max_length=30, verbose_name='Código')
    description_product = models.CharField(max_length=200, verbose_name='Descripción')
    process = models.ForeignKey(Process, verbose_name='Proceso', on_delete=models.CASCADE)
    enable_product = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.code_product) + ' '  + str(self.description_product)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'Product'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Product, self).save(*args, **kwargs)


# Etapas
class Stage(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    stage_name = models.CharField(max_length=100, verbose_name='Etapa')
    stage_code = models.CharField(max_length=20, verbose_name='Código')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Proceso')
    enable_stage = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.stage_name) + ' - ' + str(self.product.description_product)

    class Meta:
        verbose_name = 'Stage'
        verbose_name_plural = 'Stages'
        db_table = 'Stage'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Stage, self).save(*args, **kwargs)


# Puntos de Muestreo
class SamplePoint(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sample_point_code = models.CharField(max_length=30, verbose_name='Código')
    sample_point_name = models.CharField(max_length=100, verbose_name='Punto de Muestreo')
    sample_frequency = models.SmallIntegerField(verbose_name='Frecuencia de Muestreo')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, verbose_name='Etapa')
    enable_point = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.sample_point_name) + ' - ' + str(self.stage.stage_name)

    class Meta:
        verbose_name = 'SamplePoint'
        verbose_name_plural = 'SamplePoints'
        db_table = 'SamplePoint'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SamplePoint, self).save(*args, **kwargs)
