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


# Métodos Analíticos
class AnalyticalMethod(BaseModel):
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


# Soluciones para Métodos Analíticos
class AnalyticalMethodSolution(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    solution = models.ForeignKey(SolutionBase, verbose_name='Solución', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.solution)

    class Meta:
        verbose_name = 'AnalyticalMethodSolution'
        verbose_name_plural = 'AnalyticalMethodSolutions'
        db_table = 'AnalyticalMethodSolution'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodSolution, self).save(*args, **kwargs)


# Soluciones Estándares para Métodos Analíticos
class AnalyticalMethodSolutionStd(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    solution_std = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.solution_std)

    class Meta:
        verbose_name = 'AnalyticalMethodSolutionStd'
        verbose_name_plural = 'AnalyticalMethodSolutionStds'
        db_table = 'AnalyticalMethodSolutionStd'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodSolutionStd, self).save(*args, **kwargs)


# Reactivos para Métodos Analíticos
class AnalyticalMethodReagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    reagent = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.reagent)

    class Meta:
        verbose_name = 'AnalyticalMethodReagent'
        verbose_name_plural = 'AnalyticalMethodReagents'
        db_table = 'AnalyticalMethodReagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodReagent, self).save(*args, **kwargs)


# Equipos para Métodos Analíticos
class AnalyticalMethodEquipment(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    equipment_instrumental = models.ForeignKey(EquipmentInstrumental, verbose_name='Equipo Instrumental', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.equipment_instrumental)

    class Meta:
        verbose_name = 'AnalyticalMethodEquipment'
        verbose_name_plural = 'AnalyticalMethodEquipments'
        db_table = 'AnalyticalMethodEquipment'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodEquipment, self).save(*args, **kwargs)


# Material Instrumental para Métodos Analíticos
class AnalyticalMethodMaterial(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    material_instrumental = models.ForeignKey(MaterialInstrumental, verbose_name='Material Instrumental', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.material_instrumental)

    class Meta:
        verbose_name = 'AnalyticalMethodMaterialInstrumental'
        verbose_name_plural = 'AnalyticalMethodMaterialInstrumentals'
        db_table = 'AnalyticalMethodMaterialInstrumental'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodMaterial, self).save(*args, **kwargs)


# Procedimiento de metodos Analítico
class AnalyticalMethodProcedure(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analitico', on_delete=models.CASCADE)
    procedure = models.TextField(verbose_name='Procedimiento')
    step_procedure = models.PositiveSmallIntegerField(verbose_name='Paso N°')

    def __str__(self):
        return str(self.procedure)

    class Meta:
        verbose_name = 'AnalyticalMethodProcedure'
        verbose_name_plural = 'AnalyticalMethodProcedures'
        db_table = 'AnalyticalMethodProcedure'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodProcedure, self).save(*args, **kwargs)


# Cálculo de concentración de muestra
class AnalyticalMethodCalculate(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analítico', on_delete=models.CASCADE)
    calculate_description = models.CharField(max_length=100, verbose_name='Descripción del Cálculo', null=True, blank=True)
    unit_measure_calculate = models.CharField(max_length=10, verbose_name='Unidad a Calcular', null=True, blank=True)
    volumen_std = models.CharField(max_length=100, verbose_name='Variable Volúmen Estándar', null=True, blank=True)
    variable = models.CharField(max_length=100, verbose_name='Variable', null=True, blank=True)
    factor = models.FloatField(verbose_name='Constante', null=True, blank=True)
    sample_quantity = models.CharField(max_length=50, verbose_name='Variable Muestra', null=True, blank=True)
    position = models.CharField(max_length=15, verbose_name='Posición en Ecuación', null=True, blank=True)

    def __str__(self):
        return str(self.calculate_description)

    class Meta:
        verbose_name = 'AnalyticalMethodCalculate'
        verbose_name_plural = 'AnalyticalMethodCalculates'
        db_table = 'AnalyticalMethodCalculate'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodCalculate, self).save(*args, **kwargs)


# Cálculos de Relacionados
class AnalyticalMethodCalculateRelation(BaseModel):
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

    def __str__(self):
        return str(self.calculate_description_relation)

    class Meta:
        verbose_name = 'AnalyticalMethodCalculateRelation'
        verbose_name_plural = 'AnalyticalMethodCalculateRelations'
        db_table = 'AnalyticalMethodCalculateRelation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(AnalyticalMethodCalculateRelation, self).save(*args, **kwargs)


# Soluciones Estándares para Retrovaloración
class SolutionStdBackValuation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    analytical_method = models.ForeignKey(AnalyticalMethod, verbose_name='Método Analítico', on_delete=models.CASCADE)
    solution_std = models.ForeignKey(SolutionStdBase, verbose_name='Solución Estándar', on_delete=models.CASCADE)
    volume_std_back = models.FloatField(verbose_name='Volumen Estándar (mL)', blank=True, null=True)

    def __str__(self):
        return str(self.solution_std)

    class Meta:
        verbose_name = 'SolutionStdBackValuation'
        verbose_name_plural = 'SolutionStdBackValuations'
        db_table = 'SolutionStdBackValuation'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(SolutionStdBackValuation, self).save(*args, **kwargs)
