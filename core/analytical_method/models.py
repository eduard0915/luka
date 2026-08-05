"""Modelos de la aplicación de métodos analíticos.

Define las entidades para la gestión de métodos analíticos, incluyendo
soluciones, reactivos, equipos, materiales, procedimientos y cálculos.
"""

import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Site
from core.equipment.models import EquipmentInstrumental, MaterialInstrumental
from core.laboratory.models import Laboratory
from core.models import BaseModel
from core.reagent.models import Reagent
from core.solution.models import SolutionBase, SolutionStdBase
from core.user.models import User


class AnalyticalMethod(BaseModel):
    """Modelo que representa un método analítico con sus parámetros y configuración."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_analytical_method = models.CharField(max_length=250, verbose_name='Descripción')
    code_analytical_method  = models.CharField(max_length=20, verbose_name='Id')
    enable_analytical_method = models.BooleanField(default=True, verbose_name='Habilitado')
    sample_size = models.FloatField(verbose_name='Tamaño de Muestra (g)')
    type_method = models.CharField(verbose_name='Tipo de Método', max_length=100)
    laboratory = models.ForeignKey(Laboratory, verbose_name='Laboratorio', on_delete=models.CASCADE)
    sig_figs_result = models.PositiveSmallIntegerField(default=2, verbose_name='Cifras Significativas')
    version = models.PositiveSmallIntegerField(default=1, verbose_name='Versión')

    def __str__(self):
        """Retorna la representación en texto del método analítico (código + descripción)."""
        return str(self.code_analytical_method) + ' '  + str(self.description_analytical_method)

    class Meta:
        verbose_name = 'AnalyticalMethod'
        verbose_name_plural = 'AnalyticalMethods'
        db_table = 'AnalyticalMethod'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el método analítico asignando el usuario de creación o actualización."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethod, self).save(*args, **kwargs)


class AnalyticalMethodSolution(BaseModel):
    """Modelo que relaciona una solución con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    solution = models.ForeignKey(SolutionBase, verbose_name='Solución', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna la solución asociada al método analítico."""
        return str(self.solution)

    class Meta:
        verbose_name = 'AnalyticalMethodSolution'
        verbose_name_plural = 'AnalyticalMethodSolutions'
        db_table = 'AnalyticalMethodSolution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación solución-método analítico asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodSolution, self).save(*args, **kwargs)


class AnalyticalMethodSolutionStd(BaseModel):
    """Modelo que relaciona una solución estándar con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    solution_std = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna la solución estándar asociada al método analítico."""
        return str(self.solution_std)

    class Meta:
        verbose_name = 'AnalyticalMethodSolutionStd'
        verbose_name_plural = 'AnalyticalMethodSolutionStds'
        db_table = 'AnalyticalMethodSolutionStd'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación solución estándar-método analítico asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodSolutionStd, self).save(*args, **kwargs)


class AnalyticalMethodReagent(BaseModel):
    """Modelo que relaciona un reactivo con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    reagent = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna el reactivo asociado al método analítico."""
        return str(self.reagent)

    class Meta:
        verbose_name = 'AnalyticalMethodReagent'
        verbose_name_plural = 'AnalyticalMethodReagents'
        db_table = 'AnalyticalMethodReagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación reactivo-método analítico asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodReagent, self).save(*args, **kwargs)


class AnalyticalMethodEquipment(BaseModel):
    """Modelo que relaciona un equipo instrumental con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna el equipo instrumental asociado al método analítico."""
        return str(self.equipment_instrumental)

    class Meta:
        verbose_name = 'AnalyticalMethodEquipment'
        verbose_name_plural = 'AnalyticalMethodEquipments'
        db_table = 'AnalyticalMethodEquipment'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación equipo-método analítico asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodEquipment, self).save(*args, **kwargs)


class AnalyticalMethodMaterial(BaseModel):
    """Modelo que relaciona un material instrumental con un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    material_instrumental = models.ForeignKey(MaterialInstrumental, verbose_name='Material Instrumental', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna el material instrumental asociado al método analítico."""
        return str(self.material_instrumental)

    class Meta:
        verbose_name = 'AnalyticalMethodMaterialInstrumental'
        verbose_name_plural = 'AnalyticalMethodMaterialInstrumentals'
        db_table = 'AnalyticalMethodMaterialInstrumental'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la relación material-método analítico asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodMaterial, self).save(*args, **kwargs)


class AnalyticalMethodProcedure(BaseModel):
    """Modelo que almacena los pasos del procedimiento de un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    procedure = models.TextField(verbose_name='Procedimiento')
    step_procedure = models.PositiveSmallIntegerField(verbose_name='Paso N°')

    def __str__(self):
        """Retorna el texto del procedimiento."""
        return str(self.procedure)

    class Meta:
        verbose_name = 'AnalyticalMethodProcedure'
        verbose_name_plural = 'AnalyticalMethodProcedures'
        db_table = 'AnalyticalMethodProcedure'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el paso del procedimiento asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodProcedure, self).save(*args, **kwargs)


class AnalyticalMethodCalculate(BaseModel):
    """Modelo que define los cálculos de concentración de muestra para un método analítico."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analítico', on_delete=models.CASCADE)
    calculate_description = models.CharField(max_length=100, verbose_name='Descripción del Cálculo', null=True, blank=True)
    unit_measure_calculate = models.CharField(max_length=10, verbose_name='Unidad a Calcular', null=True, blank=True)
    volumen_std = models.CharField(max_length=100, verbose_name='Variable Volúmen Estándar', null=True, blank=True)
    variable = models.CharField(max_length=100, verbose_name='Variable', null=True, blank=True)
    factor = models.FloatField(verbose_name='Constante', null=True, blank=True)
    sample_quantity = models.CharField(max_length=50, verbose_name='Variable Muestra', null=True, blank=True)
    position = models.CharField(max_length=15, verbose_name='Posición en Ecuación', null=True, blank=True)
    subtract_blank = models.BooleanField(default=False, verbose_name='Restar Blanco?')

    def __str__(self):
        """Retorna la descripción del cálculo."""
        return f'{self.calculate_description} {self.unit_measure_calculate}'

    class Meta:
        verbose_name = 'AnalyticalMethodCalculate'
        verbose_name_plural = 'AnalyticalMethodCalculates'
        db_table = 'AnalyticalMethodCalculate'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el cálculo asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodCalculate, self).save(*args, **kwargs)


class DependentCalculation(BaseModel):
    """Modelo para asignar consecutivo de cálculo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    calcule_description = models.CharField(max_length=100, verbose_name='Nombre del Calculo')
    product = models.ForeignKey('product.Product', verbose_name='Producto', on_delete=models.CASCADE)
    consecutive = models.PositiveSmallIntegerField(verbose_name='Consecutivo')

    def __str__(self):
        """Retorna la descripción del cálculo."""
        return str(self.calcule_description)

    class Meta:
        verbose_name = 'DependentCalculation'
        verbose_name_plural = 'DependentCalculations'
        db_table = 'DependentCalculation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el cálculo asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(DependentCalculation, self).save(*args, **kwargs)


OPERATION = [
    ('multiply', 'Multiplicar (×)'),
    ('add', 'Sumar (+)'),
    ('subtract', 'Restar (−)'),
    ('divide', 'Dividir (÷)'),
]


class AnalyticalMethodCalculateRelation(BaseModel):
    """Modelo que define cálculos relacionados con productos y métodos analíticos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    product = models.ForeignKey('product.Product', verbose_name='Producto', on_delete=models.CASCADE, null=True, blank=True)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE, null=True, blank=True)
    analytical_method_calculate = models.ForeignKey(
        AnalyticalMethodCalculate, verbose_name='Calculo Relacionado', on_delete=models.CASCADE, null=True, blank=True)
    calculate_description_relation = models.CharField(max_length=100, verbose_name='Descripción del Cálculo')
    unit_measure_calculate = models.CharField(max_length=10, verbose_name='Unidad a Calcular')
    volumen_std = models.CharField(max_length=100, verbose_name='Volúmen Estándar', null=True, blank=True)
    factor = models.FloatField(verbose_name='Constante', null=True, blank=True)
    sample_quantity = models.CharField(max_length=50, verbose_name='Muestra', null=True, blank=True)
    position = models.CharField(max_length=15, verbose_name='Posición en Ecuación', null=True, blank=True)
    sig_figs = models.SmallIntegerField(verbose_name='Cifras Significativas', default=4)
    consecutive_calcule = models.ForeignKey(DependentCalculation, verbose_name='Consecutivo', on_delete=models.CASCADE, null=True, blank=True)
    calculate_relation_related = models.ForeignKey(
        'self', verbose_name='Cálculo Relacionado Add', on_delete=models.CASCADE, null=True, blank=True,
        related_name='added_in_relations')
    operation = models.CharField(
        max_length=10, choices=OPERATION, verbose_name='Operación con el Término Anterior', null=True, blank=True)
    parent = models.ForeignKey(
        'self', verbose_name='Agrupado Dentro de', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children')

    def __str__(self):
        """Retorna la descripción del cálculo relacionado con su unidad de medida."""
        label = str(self.calculate_description_relation)
        if self.unit_measure_calculate:
            label += ' ({})'.format(self.unit_measure_calculate)
        return label

    class Meta:
        verbose_name = 'AnalyticalMethodCalculateRelation'
        verbose_name_plural = 'AnalyticalMethodCalculateRelations'
        db_table = 'AnalyticalMethodCalculateRelation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda el cálculo relacionado asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodCalculateRelation, self).save(*args, **kwargs)


class SolutionStdBackValuation(BaseModel):
    """Modelo que almacena soluciones estándar usadas para retrovaloración en métodos analíticos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analítico', on_delete=models.CASCADE)
    solution_std = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    volume_std_back = models.FloatField(verbose_name='Volumen Estándar (mL)', blank=True, null=True)

    def __str__(self):
        """Retorna la solución estándar usada en la retrovaloración."""
        return str(self.solution_std)

    class Meta:
        verbose_name = 'SolutionStdBackValuation'
        verbose_name_plural = 'SolutionStdBackValuations'
        db_table = 'SolutionStdBackValuation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        """Guarda la retrovaloración asignando el usuario correspondiente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SolutionStdBackValuation, self).save(*args, **kwargs)


class HeavyMetal(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='', on_delete=models.CASCADE)
    metal_description = models.CharField(max_length=50, verbose_name='Descripción Metal')
    unit_measure = models.CharField(max_length=10, verbose_name='Unidad a Calcular')
    detection_limit = models.FloatField(verbose_name='Limite de Detección', null=True, blank=True)
    quantification_limit = models.FloatField(verbose_name='Limite de Cuantificación', null=True, blank=True)

    def __str__(self):
        return str(self.metal_description)

    class Meta:
        verbose_name = 'HeavyMetal'
        verbose_name_plural = 'HeavyMetals'
        db_table = 'HeavyMetal'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(HeavyMetal, self).save(*args, **kwargs)
