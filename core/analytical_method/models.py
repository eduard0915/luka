import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Site
from core.laboratory.models import Laboratory
from core.models import BaseModel
from core.product.models import Product
from core.user.models import User


# Métodos Analíticos
class AnalyticalMethod(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_analytical_method = models.CharField(max_length=250, verbose_name='Descripción')
    code_analytical_method  = models.CharField(max_length=20, verbose_name='Código')
    enable_analytical_method = models.BooleanField(default=True, verbose_name='Habilitado')
    sample_size = models.FloatField(verbose_name='Tamaño de Muestra (g)')
    type_method = models.CharField(verbose_name='Tipo de Método', max_length=100)
    laboratory = models.ForeignKey(Laboratory, verbose_name='Laboratorio', on_delete=models.CASCADE)
    sig_figs_result = models.PositiveSmallIntegerField(default=2, verbose_name='Cifras Significativas')

    def __str__(self):
        return str(self.code_analytical_method) + ' '  + str(self.description_analytical_method)

    class Meta:
        verbose_name = 'AnalyticalMethod'
        verbose_name_plural = 'AnalyticalMethods'
        db_table = 'AnalyticalMethod'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethod, self).save(*args, **kwargs)
