import uuid

from crum import get_current_user
from django.db import models, transaction
from django.utils import timezone

from core.models import BaseModel
from core.reagent.models import Reagent, InventoryReagent
from core.user.models import User


# Generador de códigos de soluciones
def code_solution_generator():
    # Obtener la fecha actual en la zona horaria local
    now = timezone.localtime(timezone.now())
    today = now.date()
    today_str = now.strftime('%Y%m%d')

    # Buscar el último registro del día actual
    with transaction.atomic():
        last_sln = Solution.objects.filter(
            date_creation__date=today
        ).select_for_update().order_by('-date_creation').first()

        if not last_sln:
            # Primer registro del día
            return f'SLN-{today_str}-1'

        # Extraer el número secuencial del código existente
        code_parts = last_sln.code_solution.split('-')
        current_number = int(code_parts[2])
        new_number = current_number + 1

        return f'SLN-{today_str}-{new_number}'


# Generador de códigos de soluciones Estándares
def code_solution_std_generator():
    # Obtener la fecha actual en la zona horaria local
    now = timezone.localtime(timezone.now())
    today = now.date()
    today_str = now.strftime('%Y%m%d')

    # Buscar el último registro del día actual
    with transaction.atomic():
        last_sln = SolutionStd.objects.filter(
            date_creation__date=today
        ).select_for_update().order_by('-date_creation').first()

        if not last_sln:
            # Primer registro del día
            return f'STD-{today_str}-1'

        # Extraer el número secuencial del código existente
        code_parts = last_sln.code_solution_std.split('-')
        current_number = int(code_parts[2])
        new_number = current_number + 1

        return f'STD-{today_str}-{new_number}'


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
    quantity_reagent = models.FloatField(verbose_name='Cant. Reactivo')
    quantity_solvent = models.FloatField(verbose_name='Solvente (mL)', null=True, blank=True)
    preparated_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE)
    standardizable = models.BooleanField(verbose_name='Estandarizable', default=False)
    average_concentration = models.FloatField(verbose_name='Media', null=True, blank=True)
    deviation_std = models.FloatField(verbose_name='Media', null=True, blank=True)
    coefficient_variation = models.FloatField(verbose_name='Coeficiente de Variación', null=True, blank=True)

    def __str__(self):
        return str(self.solute_reagent.reagent) + ' ' + str(self.concentration) + str(self.concentration_unit) + ' - ' + str(self.code_solution)

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
        db_table = 'Solution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        if self.quantity_reagent:
            self.quantity_reagent = round(self.quantity_reagent, self.solute_reagent.reagent.sig_figs_solution)

        if self.quantity_solvent:
            self.quantity_solvent = round(self.quantity_solvent, self.solute_reagent.reagent.sig_figs_solution)

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Solution, self).save(*args, **kwargs)


# Soluciones Estándares
class SolutionStd(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_std = models.ForeignKey(InventoryReagent, verbose_name='Estándar', on_delete=models.CASCADE, related_name='solute_std')
    solvent_reagent = models.ForeignKey(InventoryReagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent_std', null=True, blank=True)
    code_solution_std = models.CharField(max_length=20, verbose_name='Código', default=code_solution_std_generator)
    concentration_std = models.FloatField(verbose_name='Concentración')
    concentration_unit = models.CharField(max_length=4, verbose_name='Unidad Conc.')
    preparation_std_date = models.DateField(verbose_name='Fecha de Preparación', null=True, blank=True)
    expire_std_date_solution = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_solution_std = models.FloatField(verbose_name='Cant. a Preparar (mL)')
    quantity_std = models.FloatField(verbose_name='Cantidad de Estándar')
    quantity_solvent = models.FloatField(verbose_name='Solvente (mL)', null=True, blank=True)
    preparated_std_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.solute_std.reagent) + ' ' + str(self.concentration_std) + str(self.concentration_unit) + ' - ' + str(self.code_solution_std)

    class Meta:
        verbose_name = 'SolutionStd'
        verbose_name_plural = 'SolutionSTDs'
        db_table = 'SolutionStd'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        if self.quantity_std:
            self.quantity_std = round(self.quantity_std, self.solute_std.reagent.sig_figs_solution)

        if self.quantity_solvent:
            self.quantity_solvent = round(self.quantity_solvent, self.solute_std.reagent.sig_figs_solution)

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SolutionStd, self).save(*args, **kwargs)


# Estandarización de soluciones
class StandarizationSolution(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solution = models.ForeignKey(Solution, verbose_name='Solución', on_delete=models.CASCADE)
    standard_sln = models.ForeignKey(InventoryReagent, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    quantity_solution = models.FloatField(verbose_name='mL de Solución')
    concentration_sln = models.FloatField(verbose_name='Concentración Sln')
    quantity_standard = models.FloatField(verbose_name='mL Estándar')
    standardized_by = models.ForeignKey(User, verbose_name='Realizado por', on_delete=models.CASCADE)
    standarization_date = models.DateField(verbose_name='Fecha de Estandarización')

    def __str__(self):
        return str(self.quantity_standard)

    class Meta:
        verbose_name = 'StandarizationSolution'
        verbose_name_plural = 'StandarizationSolutions'
        db_table = 'StandarizationSolution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()

        # significant_figures = None
        # if (self.solute_reagent and self.solute_reagent.reagent and
        #     self.solute_reagent.reagent.site and self.solute_reagent.reagent.site.company):
        #     significant_figures = self.solute_reagent.reagent.site.company.sig_figs_solution
        #
        # if self.quantity_reagent and significant_figures is not None:
        #     self.quantity_reagent = round(self.quantity_reagent, significant_figures)
        #
        # if self.quantity_solvent and significant_figures is not None:
        #     self.quantity_solvent = round(self.quantity_solvent, significant_figures)

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(StandarizationSolution, self).save(*args, **kwargs)
