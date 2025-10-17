import uuid

from crum import get_current_user
from django.db import models

from core.models import BaseModel
from core.reagent.models import Reagent
from core.user.models import User


class Solution(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reagent = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE)
    code_solution = models.CharField(max_length=15, verbose_name='Código')
    concentration = models.PositiveSmallIntegerField(verbose_name='Concentración')
    concentration_unit = models.CharField(max_length=4, verbose_name='Unidad de Medida')
    preparation_date = models.DateField(verbose_name='Fecha de Preparación')
    expire_date_solution = models.DateField(verbose_name='Fecha de Vencimiento')
    quantity_solution = models.FloatField(verbose_name='Cantidad (mL)')
    preparated_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.reagent) + ' ' + str(self.concentration) + str(self.concentration_unit)

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
        db_table = 'Solution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Solution, self).save(*args, **kwargs)
