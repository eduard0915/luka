from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

from core.sampling.models import SamplingProcess, SamplingAnalysis, SamplingAnalysisProcessing
from core.solution.models import TransactionSolutionStd, SolutionStd


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

    if not analytical_methods:
        return

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

        # Determinar cumplimiento
        sampling_point = _get_sampling_point(sampling_analysis.sampling_process)

        if sampling_point:
            sampling_analysis.comply = _check_compliance(
                sampling_point,
                sampling_analysis.analytical_method,
                instance.concentration_sample
            )

        # Guardar análisis
        sampling_analysis.save(update_fields=['average_concentration', 'comply'])

        # Actualizar inventario
        _update_solution_inventory(instance)

        # Crear transacción
        _create_solution_transaction(instance)


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

    # Usar Decimal para comparaciones numéricas precisas
    value = Decimal(str(concentration_value))
    lower_dec = Decimal(str(lower)) if lower is not None else None
    upper_dec = Decimal(str(upper)) if upper is not None else None

    # Lógica de verificación simplificada
    if lower_dec is not None and upper_dec is not None:
        return 'Cumple' if lower_dec <= value <= upper_dec else 'No Cumple'
    elif lower_dec is not None:
        return 'Cumple' if value >= lower_dec else 'No Cumple'
    elif upper_dec is not None:
        return 'Cumple' if value <= upper_dec else 'No Cumple'

    return None


def _update_solution_inventory(instance):
    """
    Actualiza el inventario de la solución estándar.
    Usa select_for_update para evitar race conditions.
    """
    std_solution = SolutionStd.objects.select_for_update().get(
        pk=instance.standard_solution_id
    )

    # Usar Decimal para operaciones numéricas precisas
    current_quantity = Decimal(str(std_solution.quantity_solution_std))
    used_quantity = Decimal(str(instance.quantity_standard))
    new_quantity = current_quantity - used_quantity

    std_solution.quantity_solution_std = round(new_quantity, 2)
    std_solution.save(update_fields=['quantity_solution_std'])


def _create_solution_transaction(instance):
    """Crea el registro de transacción de la solución estándar."""
    TransactionSolutionStd.objects.create(
        solution_std_inventory_id=instance.standard_solution_id,
        type_transaction='Uso - Análisis de Muestra',
        date_transaction=timezone.localdate(),
        detail_transaction=f'Muestra {instance.sample_analysis.sampling_process}',
        quantity=instance.quantity_standard,
        user_transaction_id=instance.analyzed_by_id,
    )
