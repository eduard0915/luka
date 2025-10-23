import uuid

from crum import get_current_user
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from core.reagent.models import Reagent, InventoryReagent
from core.user.models import User


# Generador de códigos de soluciones
def code_solution_generator():
    today = timezone.now().strftime('%Y%m%d')
    last_sln = Solution.objects.order_by('date_creation').last()
    if not last_sln or last_sln.date_creation.strftime('%Y%m%d') != timezone.now().strftime('%Y%m%d'):
        return 'SLN-' + today + '-' + '1'
    code_sln = last_sln.code_solution
    code_sln_int = int(code_sln.split('-')[2])
    new_code_sln_int = code_sln_int + 1
    new_code_sln = 'SLN-' + today + '-' + str(new_code_sln_int)
    return new_code_sln


# Soluciones
class Solution(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_reagent = models.ForeignKey(InventoryReagent, verbose_name='Reactivo', on_delete=models.CASCADE, related_name='solute')
    solvent_reagent = models.ForeignKey(InventoryReagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent')
    code_solution = models.CharField(max_length=20, verbose_name='Código', default=code_solution_generator)
    concentration = models.FloatField(verbose_name='Concentración')
    concentration_unit = models.CharField(max_length=4, verbose_name='Unidad Conc.')
    preparation_date = models.DateField(verbose_name='Fecha de Preparación', null=True, blank=True)
    expire_date_solution = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_solution = models.FloatField(verbose_name='Cant. a Preparar (mL)')
    quantity_reagent = models.FloatField(verbose_name='Cant. Reactivo (mL)')
    quantity_solvent = models.FloatField(verbose_name='Solvente (mL)', null=True, blank=True)
    preparated_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.solute_reagent.reagent) + ' ' + str(self.concentration) + str(self.concentration_unit) + ' - ' + str(self.code_solution)

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
        db_table = 'Solution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        significant_figures = None
        if (self.solute_reagent and self.solute_reagent.reagent and
            self.solute_reagent.reagent.site and self.solute_reagent.reagent.site.company):
            significant_figures = self.solute_reagent.reagent.site.company.sig_figs_solution

        if self.quantity_reagent and significant_figures is not None:
            self.quantity_reagent = round(self.quantity_reagent, significant_figures)

        if self.quantity_solvent and significant_figures is not None:
            self.quantity_solvent = round(self.quantity_solvent, significant_figures)

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Solution, self).save(*args, **kwargs)
