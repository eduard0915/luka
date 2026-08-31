"""Señales de Django para la aplicación de muestreo."""

from decimal import Decimal

from django.db import transaction
from django.db.models.aggregates import Avg, StdDev
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation
from core.product.models import SpecificationProduct
from core.sampling.models import *
from core.sampling.services import send_oss_notification_email
from core.solution.models import SolutionStd, TransactionSolutionStd


@receiver(pre_save, sender=SamplingAnalysis)
def track_sampling_analysis_comply(sender, instance, **kwargs):
    """Registra el valor previo de comply para detectar cambios a 'No Cumple'."""
    try:
        instance._previous_comply = SamplingAnalysis.objects.values_list(
            'comply', flat=True).get(pk=instance.pk)
    except SamplingAnalysis.DoesNotExist:
        instance._previous_comply = None


@receiver(post_save, sender=SamplingAnalysis)
def send_oss_notification_on_comply(sender, instance, created, **kwargs):
    """Envía correo de notificación cuando el concepto cambia a 'No Cumple'."""
    previous = getattr(instance, '_previous_comply', None)
    if instance.comply == 'No Cumple' and previous != 'No Cumple':
        send_oss_notification_email(instance)


@receiver(post_save, sender=SamplingProcess)
def create_sampling_analysis(sender, instance, created, **kwargs):
    """Crea los análisis de muestra cuando un proceso de muestreo es confirmado."""
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

    # Crear análisis en bloque para mejor rendimiento
    # Primero verificar cuáles ya existen
    existing_methods = set(
        SamplingAnalysis.objects.select_related('sampling_process', 'analytical_method').filter(
            sampling_process=instance,
            analytical_method__in=analytical_methods
        ).values_list('analytical_method_id', flat=True)
    )

    # Crear solo los que no existen
    new_analyses = [
        SamplingAnalysis(
            sampling_process=instance,
            analytical_method=method
        )
        for method in analytical_methods
        if method.id not in existing_methods
    ]

    if new_analyses:
        SamplingAnalysis.objects.bulk_create(
            new_analyses,
            ignore_conflicts=True  # Por si acaso hay race conditions
        )

    if instance.group_sampling:
        product_id = instance.group_sampling.sampling_point.product.id
    else:
        product_id = instance.point_sampling.product.id

    calculate_relations = AnalyticalMethodCalculateRelation.objects.select_related('product').filter(
        product=product_id).exclude(calculate_description_relation__in=[None, ''])

    existing_relations = set(
        SamplingAnalysis.objects.select_related('sampling_process', 'analytical_method_relation').filter(
            sampling_process=instance,
            analytical_method_relation__in=calculate_relations
        ).values_list('analytical_method_relation_id', flat=True)
    )

    new_analyses_rel = [
        SamplingAnalysis(
            sampling_process=instance,
            analytical_method_relation=calculate,
        )
        for calculate in calculate_relations
        if calculate.id not in existing_relations
    ]

    if new_analyses_rel:
        SamplingAnalysis.objects.bulk_create(
            new_analyses_rel,
            ignore_conflicts=True  # Por si acaso hay race conditions
        )


@receiver(post_save, sender=SamplingAnalysisProcessing)
def update_sampling_analysis(sender, instance, **kwargs):
    """Actualiza el análisis de muestra cuando se registra un procesamiento."""
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
    """Obtiene el punto de muestreo de forma consistente desde el proceso."""
    if sampling_process.group_sampling:
        return sampling_process.group_sampling.sampling_point
    return sampling_process.point_sampling

def _check_compliance(sampling_point, analytical_method, concentration_value):
    """Determina si la concentración cumple con las especificaciones del producto."""
    # Buscar especificación con select_related para optimización
    specification = sampling_point.specification.select_related('method_test__analytical_method').filter(
        method_test__analytical_method=analytical_method).first()

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
    """Actualiza el inventario de la solución estándar usando bloqueo pesimista."""
    if solution_id is None or quantity_to_subtract is None or quantity_to_subtract <= 0:
        return

    std_solution = SolutionStd.objects.select_for_update().get(pk=solution_id)

    # Usar Decimal para operaciones numéricas precisas
    current_quantity = Decimal(str(std_solution.quantity_available_std))
    used_quantity = Decimal(str(quantity_to_subtract))
    new_quantity = current_quantity - used_quantity

    std_solution.quantity_available_std = float(round(new_quantity, 2))
    std_solution.save(update_fields=['quantity_available_std'])


def _create_solution_transaction(solution_id, quantity, user_id, detail_text):
    """Crea el registro de transacción de la solución estándar por uso en análisis."""
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
    """Crea un procesamiento de análisis cuando se registran milimoles reaccionados."""
    if not created:
        return

    with transaction.atomic():
        analysis = instance.sampling_analysis
        analytical_method_id = analysis.analytical_method.id
        
        # Obtener variables de cálculo para el método
        var_num = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(
            analytical_method_id=analytical_method_id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(
            analytical_method_id=analytical_method_id, position='Denominador')
        base_calc = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(
            analytical_method_id=analytical_method_id).first()

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
                f'Volumetría por Retroceso - Muestra {instance.sampling_analysis.sampling_process}'
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


@receiver(post_save, sender=SamplingAnalysisProcessingRelation)
def create_processing_relation(sender, instance, created, **kwargs):
    """Actualiza el análisis con los valores calculados de la relación de procesamiento."""

    analysis = instance.sampling_analysis
    if not analysis:
        analysis = SamplingAnalysis.objects.filter(analytical_method_relation=instance.analytical_method_calculate_relation).first()
    if not analysis:
        return

    spc = SpecificationProduct.objects.filter(method_test_relacional=instance.analytical_method_calculate_relation).first()
    if not spc and analysis.sampling_process:
        sampling_process = analysis.sampling_process
        product = (
            sampling_process.point_sampling.product
            if sampling_process.point_sampling
            else sampling_process.group_sampling.sampling_point.product
        )
        if product:
            spc = SpecificationProduct.objects.filter(
                product=product,
                method_test_relacional=instance.analytical_method_calculate_relation
            ).first()

    previous_analysis = SamplingAnalysisProcessingRelation.objects.select_related(
        'analytical_method_calculate_relation').filter(
        analytical_method_calculate_relation=instance.analytical_method_calculate_relation)

    stats = previous_analysis.aggregate(std=StdDev('calcule'), avg=Avg('calcule'))

    analysis.standard_deviation = round(stats['std'], 4) or 0
    analysis.coefficient_variation = round(stats['std'] / stats['avg'], 2) or 0
    analysis.average_concentration = round(stats['avg'], 4) or round(instance.calcule, 4)
    analysis.date_analysis = timezone.now()

    if spc:
        if spc.lower_limit_prod and spc.upper_limit_prod:
            if spc.lower_limit_prod <= instance.calcule <= spc.upper_limit_prod:
                analysis.comply = 'Cumple'
            else:
                analysis.comply = 'No Cumple'
        elif spc.lower_limit_prod and not spc.upper_limit_prod:
            if instance.calcule >= spc.lower_limit_prod:
                analysis.comply = 'Cumple'
            else:
                analysis.comply = 'No Cumple'
        elif not spc.lower_limit_prod and spc.upper_limit_prod:
            if instance.calcule <= spc.upper_limit_prod:
                analysis.comply = 'Cumple'
            else:
                analysis.comply = 'No Cumple'
    else:
        analysis.comply = 'No aplica'

    analysis.save()
