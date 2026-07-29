"""Modelos de datos para el módulo de soluciones del sistema LIMS.

Define las entidades Solution, SolutionBase, SolutionStd, SolutionStdBase,
Standardization, StandardizationSolution, TransactionSolution y TransactionSolutionStd.
"""

import uuid

from crum import get_current_user
from django.db import models, transaction
from django.utils import timezone

from core.models import BaseModel
from core.reagent.models import Reagent, InventoryReagent
from core.user.models import User
from core.laboratory.models import Laboratory


def code_solution_generator():
    """Genera un código secuencial para soluciones con formato SLN-YYYYMMDD-N."""
    # Obtener la fecha actual en la zona horaria local
    today = timezone.localdate()
    today_str = today.strftime('%Y%m%d')

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
    """Genera un código secuencial para soluciones estándar con formato STD-YYYYMMDD-N."""
    # Obtener la fecha actual en la zona horaria local
    today = timezone.localdate()
    today_str = today.strftime('%Y%m%d')

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


class SolutionBase(BaseModel):
    """Define la plantilla base para la preparación de soluciones con soluto, solvente y concentración."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_reagent_base = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE, related_name='solute_base')
    solvent_reagent_base = models.ForeignKey(Reagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent_base')
    concentration_base = models.FloatField(verbose_name='Concentración')
    concentration_unit_base = models.CharField(max_length=4, verbose_name='Unidad Conc.')
    enable_solution = models.BooleanField(verbose_name='Habilitado', default=True)
    stability_solution = models.PositiveSmallIntegerField(
        verbose_name='Días Estabilidad en Solución', null=True, blank=True)
    standardizable = models.BooleanField(verbose_name='Estandarizable', default=False)

    def __str__(self):
        """Retorna la representación en texto con el reactivo y la concentración."""
        return str(self.solute_reagent_base.description_reagent) + ' ' + str(self.concentration_base) + str(self.concentration_unit_base)

    class Meta:
        verbose_name = 'SolutionBase'
        verbose_name_plural = 'SolutionsBase'
        db_table = 'SolutionBase'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la solución base asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SolutionBase, self).save(*args, **kwargs)


class Solution(BaseModel):
    """Representa una solución preparada en el laboratorio con su concentración, cantidades y estado."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_reagent = models.ForeignKey(InventoryReagent, verbose_name='Reactivo', on_delete=models.CASCADE, related_name='solute')
    solvent_reagent = models.ForeignKey(InventoryReagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent')
    solution_base = models.ForeignKey(SolutionBase, verbose_name='Solución a Preparar', on_delete=models.CASCADE)
    code_solution = models.CharField(max_length=20, verbose_name='Código', default=code_solution_generator)
    concentration = models.FloatField(verbose_name='Concentración')
    concentration_unit = models.CharField(max_length=4, verbose_name='Unidad Conc.')
    preparation_date = models.DateField(verbose_name='Fecha de Preparación', null=True, blank=True)
    expire_date_solution = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_solution = models.FloatField(verbose_name='Cant. a Preparar (mL)')
    quantity_available_sln = models.FloatField(verbose_name='Cantidad Disponible (mL)', null=True, blank=True)
    quantity_reagent = models.FloatField(verbose_name='Cant. Reactivo')
    quantity_solvent = models.FloatField(verbose_name='Solvente (mL)', null=True, blank=True)
    preparated_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE, null=True, blank=True)
    standardizable = models.BooleanField(verbose_name='Estandarizable', default=False)
    average_concentration = models.FloatField(verbose_name='Media', null=True, blank=True)
    deviation_std = models.FloatField(verbose_name='Media', null=True, blank=True)
    coefficient_variation = models.FloatField(verbose_name='Coeficiente de Variación', null=True, blank=True)
    preparation_confirmed = models.BooleanField(default=False)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, verbose_name='Laboratorio', blank=True, null=True)

    def __str__(self):
        """Retorna la representación en texto con la solución base y el código."""
        return f'{self.code_solution} - {self.solution_base} {self.quantity_available_sln}mL'

    class Meta:
        verbose_name = 'Solution'
        verbose_name_plural = 'Solutions'
        db_table = 'Solution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la solución redondeando cantidades y asignando el usuario."""
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


class SolutionStdBase(BaseModel):
    """Define la plantilla base para soluciones estándar con un reactivo certificado."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_std_base = models.ForeignKey(Reagent, verbose_name='Estándar', on_delete=models.CASCADE, related_name='solute_std_base')
    solvent_reagent_base = models.ForeignKey(Reagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent_std_base', null=True, blank=True)
    concentration_std_base = models.FloatField(verbose_name='Concentración')
    concentration_unit_base = models.CharField(max_length=4, verbose_name='Unidad Conc.')
    enable_solution_std = models.BooleanField(verbose_name='Habilitado', default=True)
    stability_solution = models.PositiveSmallIntegerField(verbose_name='Días Estabilidad en Solución', null=True, blank=True)
    standardizable = models.BooleanField(verbose_name='Estandarizable', default=False)

    def __str__(self):
        """Retorna la representación con el estándar y la concentración."""
        return str(self.solute_std_base.description_reagent) + ' ' + str(self.concentration_std_base) + str(self.concentration_unit_base)

    class Meta:
        verbose_name = 'SolutionStdBase'
        verbose_name_plural = 'SolutionsStdBase'
        db_table = 'SolutionStdBase'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la solución estándar base asignando el usuario."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SolutionStdBase, self).save(*args, **kwargs)


class SolutionStd(BaseModel):
    """Representa una solución estándar preparada a partir de un reactivo certificado."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solute_std = models.ForeignKey(InventoryReagent, verbose_name='Estándar', on_delete=models.CASCADE, related_name='solute_std')
    solvent_reagent = models.ForeignKey(InventoryReagent, verbose_name='Solvente', on_delete=models.CASCADE, related_name='solvent_std', null=True, blank=True)
    solution_std_base = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar a Preparar', on_delete=models.CASCADE)
    code_solution_std = models.CharField(max_length=20, verbose_name='Código', default=code_solution_std_generator)
    concentration_std = models.FloatField(verbose_name='Concentración', null=True, blank=True)
    concentration_unit = models.CharField(max_length=4, verbose_name='Unidad Conc.', null=True, blank=True)
    preparation_std_date = models.DateField(verbose_name='Fecha de Preparación', null=True, blank=True)
    expire_std_date_solution = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_solution_std = models.FloatField(verbose_name='Cant. a Preparar (mL)')
    quantity_std = models.FloatField(verbose_name='Cantidad de Estándar')
    quantity_solvent = models.FloatField(verbose_name='Solvente (mL)', null=True, blank=True)
    preparated_std_by = models.ForeignKey(User, verbose_name='Preparado por', on_delete=models.CASCADE, null=True, blank=True)
    preparation_confirmed = models.BooleanField(default=False)
    laboratory = models.ForeignKey(Laboratory, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Laboratorio')

    def __str__(self):
        """Retorna la representación con el reactivo, concentración, código y cantidad."""

        solution_std_base = f'{self.code_solution_std} - {self.solution_std_base}'

        if not self.preparated_std_by:
            return solution_std_base + ' - ' + f'{self.quantity_solution_std}{self.solute_std.reagent.umb}'
        else:
            return solution_std_base + ' - ' + f'{self.quantity_solution_std}mL'

    class Meta:
        verbose_name = 'SolutionStd'
        verbose_name_plural = 'SolutionSTDs'
        db_table = 'SolutionStd'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la solución estándar redondeando cantidades y asignando el usuario."""
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


class Standardization(BaseModel):
    """Configuración de estandarización que relaciona una solución con un estándar y su relación molar."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solution_std = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar', on_delete=models.CASCADE, related_name='solution_std')
    solution_base = models.ForeignKey(SolutionBase, verbose_name='Solución Base', on_delete=models.CASCADE, blank=True, null=True, related_name='solution_std_base')
    solution_std_base = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar Base', on_delete=models.CASCADE, blank=True, null=True)
    molar_relation = models.FloatField(verbose_name='Relación Molar', default=1)

    def __str__(self):
        """Retorna la relación molar de la estandarización."""
        return str(self.molar_relation)

    class Meta:
        verbose_name = 'Standardization'
        verbose_name_plural = 'Standardizations'
        db_table = 'Standardization'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la estandarización asignando el usuario."""
        user = get_current_user()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Standardization, self).save(*args, **kwargs)


class StandardizationSolution(BaseModel):
    """Registro individual de una estandarización con cantidades y concentración calculada."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solution = models.ForeignKey(Solution, verbose_name='Solución', on_delete=models.CASCADE)
    standard_solution = models.ForeignKey(SolutionStd, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    quantity_standard = models.FloatField(verbose_name=' Cantidad de Estándar')
    quantity_solution = models.FloatField(verbose_name='mL de Solución Gastados')
    concentration_sln = models.FloatField(verbose_name='Concentración Sln')
    standardized_by = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)
    standarization_date = models.DateField(verbose_name='')

    def __str__(self):
        """Retorna la cantidad de estándar utilizada."""
        return str(self.quantity_standard)

    class Meta:
        verbose_name = 'StandardizationSolution'
        verbose_name_plural = 'StandardizationSolutions'
        db_table = 'StandardizationSolution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la estandarización de solución asignando el usuario."""
        user = get_current_user()

        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(StandardizationSolution, self).save(*args, **kwargs)


class TransactionSolution(BaseModel):
    """Registro de movimientos de inventario de soluciones (entradas, salidas, usos)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solution_inventory = models.ForeignKey(Solution, verbose_name='Solución', on_delete=models.CASCADE)
    date_transaction = models.DateField(verbose_name='Fecha')
    type_transaction = models.CharField(max_length=50, verbose_name='Tipo de Registro')
    detail_transaction = models.CharField(max_length=250, verbose_name='Detalle de Registro')
    quantity = models.FloatField(verbose_name='Cantidad')
    user_transaction = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna la cantidad de la transacción."""
        return str(self.quantity)

    class Meta:
        verbose_name = 'TransactionSolution'
        verbose_name_plural = 'TransactionSolutions'
        db_table = 'TransactionSolution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la transacción de solución asignando el usuario."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(TransactionSolution, self).save(*args, **kwargs)


class TransactionSolutionStd(BaseModel):
    """Registro de movimientos de inventario de soluciones estándar (entradas, salidas, usos)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solution_std_inventory = models.ForeignKey(SolutionStd, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    date_transaction = models.DateField(verbose_name='Fecha')
    type_transaction = models.CharField(max_length=50, verbose_name='Tipo de Registro')
    detail_transaction = models.CharField(max_length=250, verbose_name='Detalle de Registro')
    quantity = models.FloatField(verbose_name='Cantidad')
    user_transaction = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna la cantidad de la transacción estándar."""
        return str(self.quantity)

    class Meta:
        verbose_name = 'TransactionSolutionStd'
        verbose_name_plural = 'TransactionSolutionStds'
        db_table = 'TransactionSolutionStd'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la transacción de solución estándar asignando el usuario."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(TransactionSolutionStd, self).save(*args, **kwargs)
