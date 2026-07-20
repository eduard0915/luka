from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from core.sampling.models import SamplingProcess, SamplingAnalysis, SamplingAnalysisProcessing, MillimoleReacted
from core.solution.models import TransactionSolutionStd, SolutionStd
from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation


# Signal para creación de especificaciones y metodos de análisis cuando el estado de la muestra es Confirmada
@receiver(post_save, sender=SamplingProcess)
def create_sampling_analysis(sender, instance, created, **kwargs):
    """
    Crea registros de SamplingAnalysis cuando un SamplingProcess es confirmado.
    Solo se ejecuta en updates (created=False) cuando el status es 'Confirmada'.
    """
    # Retornar temprano si es creación o no está confirmada
    if created or instance.status_sampling != 'Confirmada':
        return

    # Obtener sampling_point de forma más eficiente
    sampling_point = (
        instance.group_sampling.sampling_point
        if instance.group_sampling
        else instance.point_sampling
    )

    if not sampling_point:
        return

    # Usar select_related para evitar queries N+1
    specifications = sampling_point.specification.select_related(
        'method_test',
        'method_test__analytical_method'
    )

    # Recolectar métodos analíticos únicos
    analytical_methods = {
        spec.method_test.analytical_method
        for spec in specifications
        if spec.method_test and spec.method_test.analytical_method
    }

    # if not analytical_methods:
    #     return

    # Crear análisis en bloque para mejor rendimiento
    # Primero verificar cuáles ya existen
    existing_methods = set(
        SamplingAnalysis.objects.filter(
            sampling_process=instance,
            analytical_method__in=analytical_methods
        ).values_list('analytical_method_id', flat=True)
    )

    # Crear solo los que no existen
    new_analyses = [
        SamplingAnalysis(
            sampling_process=instance,
            analytical_method=method,
        )
        for method in analytical_methods
        if method.id not in existing_methods
    ]

    if new_analyses:
        SamplingAnalysis.objects.bulk_create(
            new_analyses,
            ignore_conflicts=True  # Por si acaso hay race conditions
        )

    calculate_relations = AnalyticalMethodCalculateRelation.objects.filter(
        product=instance.product).exclude(calculate_description_relation__in=[None, ''])

    print(calculate_relations)

    if calculate_relations:
        new_analyses += [
            SamplingAnalysis(
                sampling_process=instance,
                analytical_method=None,
                analytical_method_relation=relation,
            )
            for relation in calculate_relations
            if relation.id not in calculate_relations
        ]


# Signal para actualización de los análisis de una muestra
@receiver(post_save, sender=SamplingAnalysisProcessing)
def update_sampling_analysis(sender, instance, **kwargs):
    if instance.relational_calculation:
        return

    with transaction.atomic():
        sampling_analysis = SamplingAnalysis.objects.select_related(
            'sampling_process',
            'sampling_process__group_sampling__sampling_point',
            'sampling_process__point_sampling',
            'analytical_method'
        ).get(pk=instance.sample_analysis_id)

        # Actualizar concentración promedio
        sampling_analysis.average_concentration = instance.concentration_sample

        # Actualizar fecha y hora de análisis
        sampling_analysis.date_analysis = timezone.now()

        # Determinar cumplimiento
        sampling_point = _get_sampling_point(sampling_analysis.sampling_process)

        if sampling_point:
            sampling_analysis.comply = _check_compliance(
                sampling_point,
                sampling_analysis.analytical_method,
                instance.concentration_sample
            )

        # Guardar análisis
        sampling_analysis.save(update_fields=['average_concentration', 'comply', 'date_analysis'])

        # Actualizar inventario solo si hay solución estándar (análisis volumétrico)
        if instance.standard_solution_id:
            _update_solution_inventory(instance.standard_solution_id, instance.quantity_standard)

            # Crear transacción solo si hay solución estándar
            _create_solution_transaction(
                instance.standard_solution_id,
                instance.quantity_standard,
                instance.analyzed_by_id,
                f'Muestra {instance.sample_analysis.sampling_process}'
            )

def _get_sampling_point(sampling_process):
    """Helper para obtener el sampling_point de forma consistente."""
    if sampling_process.group_sampling:
        return sampling_process.group_sampling.sampling_point
    return sampling_process.point_sampling

def _check_compliance(sampling_point, analytical_method, concentration_value):
    """
    Determina si la concentración cumple con las especificaciones.

    Args:
        sampling_point: Punto de muestreo
        analytical_method: Método analítico
        concentration_value: Valor de concentración a verificar

    Returns:
        str: 'Cumple', 'No Cumple', o None
    """
    # Buscar especificación con select_related para optimización
    specification = sampling_point.specification.select_related(
        'method_test__analytical_method'
    ).filter(
        method_test__analytical_method=analytical_method
    ).first()

    if not specification:
        return None

    lower = specification.lower_limit_prod
    upper = specification.upper_limit_prod

    # Si no hay límites definidos, no se puede determinar cumplimiento
    if lower is None and upper is None:
        return None

    # Usar Decimal para comparaciones numéricas precisas
    value = Decimal(str(concentration_value))
    lower_dec = Decimal(str(lower)) if lower is not None else None
    upper_dec = Decimal(str(upper)) if upper is not None else None

    # Validación del cumplimiento según los límites disponibles
    if lower_dec is not None and upper_dec is not None:
        # Rango completo: lower <= valor <= upper
        return 'Cumple' if lower_dec <= value <= upper_dec else 'No Cumple'
    elif lower_dec is not None and upper_dec is None:
        # Solo límite inferior: valor >= lower
        return 'Cumple' if value >= lower_dec else 'No Cumple'
    elif lower_dec is None and upper_dec is not None:
        # Solo límite superior: valor <= upper
        return 'Cumple' if value <= upper_dec else 'No Cumple'
    return None

def _update_solution_inventory(solution_id, quantity_to_subtract):
    """
    Actualiza el inventario de la solución estándar.
    Usa select_for_update para evitar race conditions.
    """
    if solution_id is None or quantity_to_subtract is None or quantity_to_subtract <= 0:
        return

    std_solution = SolutionStd.objects.select_for_update().get(pk=solution_id)

    # Usar Decimal para operaciones numéricas precisas
    current_quantity = Decimal(str(std_solution.quantity_solution_std))
    used_quantity = Decimal(str(quantity_to_subtract))
    new_quantity = current_quantity - used_quantity

    std_solution.quantity_solution_std = float(round(new_quantity, 2))
    std_solution.save(update_fields=['quantity_solution_std'])


def _create_solution_transaction(solution_id, quantity, user_id, detail_text):
    """Crea el registro de transacción de la solución estándar."""
    # Solo crear transacción si hay una cantidad válida
    if solution_id is None or quantity is None or quantity <= 0:
        return

    TransactionSolutionStd.objects.create(
        solution_std_inventory_id=solution_id,
        type_transaction='Uso - Análisis de Muestra',
        date_transaction=timezone.localdate(),
        detail_transaction=detail_text,
        quantity=quantity,
        user_transaction_id=user_id,
    )


@receiver(post_save, sender=MillimoleReacted)
def create_sampling_analysis_processing_from_millimole(sender, instance, created, **kwargs):
    """
    Crea una instancia de SamplingAnalysisProcessing cuando se genera un MillimoleReacted.
    Lógica de cálculo similar a SamplingAnalysisProcessingGravimetryForm.
    """
    if not created:
        return

    with transaction.atomic():
        analysis = instance.sampling_analysis
        analytical_method_id = analysis.analytical_method.id
        
        # Obtener variables de cálculo para el método
        var_num = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Denominador')
        base_calc = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id).first()

        millimole = float(instance.millimole)
        qty_sample = float(instance.quantity_sample)
        cifras_sign = analysis.analytical_method.sig_figs_result or 2

        concentration_sample = 0
        if qty_sample > 0:
            factor_num = 1.0
            variable_num = 1.0
            sample_num = 1.0

            for num in var_num:
                if num.factor is not None:
                    factor_num *= float(num.factor)
                if num.variable is not None:
                    # En GravimetryForm usa weight_obtained, aquí usamos millimole
                    variable_num *= millimole
                if num.sample_quantity and num.sample_quantity.strip():
                    sample_num = qty_sample

            numerator = factor_num * sample_num * variable_num

            factor_den = 1.0
            variable_den = 1.0
            sample_den = 1.0

            for den in var_den:
                if den.factor is not None:
                    factor_den *= float(den.factor)
                if den.variable is not None:
                    variable_den *= millimole
                if den.sample_quantity and den.sample_quantity.strip():
                    sample_den = qty_sample

            denominator = factor_den * sample_den * variable_den
            
            if denominator != 0:
                concentration_sample = round((numerator / denominator), cifras_sign)

        # Crear instancia de SamplingAnalysisProcessing
        SamplingAnalysisProcessing.objects.create(
            sample_analysis=analysis,
            millimole_reacted=millimole,
            quantity_sample=qty_sample,
            concentration_sample=concentration_sample,
            analyzed_by=instance.user_creation,
            analyzed_date=timezone.now(),
            relational_calculation=False,
            analytical_method_calculate=base_calc,  
            weight_obtained=None,
            quantity_standard=None,
            standard_solution=None,
            analytical_method_calculate_relation=None
        )

        # Descuento de inventario y creación de transacciones para MillimoleReacted
        # Solución Adicionada
        if instance.standard_solution_add_id and instance.milliliter_std_add > 0:
            _update_solution_inventory(instance.standard_solution_add_id, instance.milliliter_std_add)
            _create_solution_transaction(
                instance.standard_solution_add_id,
                instance.milliliter_std_add,
                instance.user_creation_id,
                f'Adición para Volumetría por Retroceso - Muestra {instance.sampling_analysis.sampling_process}'
            )

        # Solución Gastada
        if instance.standard_solution_spend_id and instance.milliliter_std_spend > 0:
            _update_solution_inventory(instance.standard_solution_spend_id, instance.milliliter_std_spend)
            _create_solution_transaction(
                instance.standard_solution_spend_id,
                instance.milliliter_std_spend,
                instance.user_creation_id,
                f'Gasto en Volumetría por Retroceso - Muestra {instance.sampling_analysis.sampling_process}'
            )
