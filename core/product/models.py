import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Process, Site
from core.models import BaseModel


# Productos
class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    code_product = models.CharField(max_length=30, verbose_name='Código')
    description_product = models.CharField(max_length=200, verbose_name='Descripción')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Planta')
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


# Puntos de Muestreo
class SamplePoint(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sample_point_code = models.CharField(max_length=30, verbose_name='Código')
    sample_point_name = models.CharField(max_length=100, verbose_name='Punto de Muestreo')
    sample_frequency = models.SmallIntegerField(verbose_name='Frecuencia (Horas)', null=True, blank=True)
    sequence = models.SmallIntegerField(verbose_name='Secuencia')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    enable_point = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.sample_point_name) + ' - ' + str(self.product.description_product)

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
