"""Señales de Django para el módulo de soluciones.

Maneja el descuento automático de inventarios, el registro de
transacciones y el cálculo de estadísticas de estandarización.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F, StdDev, Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import TransactionReagent, InventoryReagent
from core.solution.models import *


# Descuento de inventario de reactivos soluto para soluciones
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solute(sender, instance, **kwargs):
    """Descuenta del inventario las cantidades de soluto y solvente usadas al confirmar una solución."""

    if instance.preparation_confirmed and instance.solvent_reagent:

        # Registro de transacciones, uso de soluto - reactivo
        InventoryReagent.objects.filter(pk=instance.solute_reagent.id).update(
            quantity_stock=round((instance.solute_reagent.quantity_stock - instance.quantity_reagent), 2))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solute_reagent.id,
            type_transaction='Uso - Preparación Sln',
            date_transaction=timezone.localdate(),
            detail_transaction='Solución ' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_reagent,
            user_transaction_id=instance.preparated_by.id,
        )

        # Registro de transacciones, uso de solvente
        InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
            quantity_stock=round((instance.solvent_reagent.quantity_stock - instance.quantity_solvent), 2))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solvent_reagent.id,
            type_transaction='Uso - Preparación Sln',
            date_transaction=timezone.localdate(),
            detail_transaction='Solución' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_solvent,
            user_transaction_id=instance.user_creation.id,
        )


# Descuento de inventario de reactivos en preparación de soluciones Estándares
@receiver(post_save, sender=SolutionStd)
def discount_reagent_transaction_std(sender, instance, **kwargs):
    """Descuenta del inventario las cantidades de soluto y solvente usadas al confirmar una solución estándar."""

    if instance.preparation_confirmed and instance.solvent_reagent:

        # Registro de transacciones, uso de soluto - reactivo
        InventoryReagent.objects.filter(pk=instance.solute_std.id).update(
            quantity_stock=round(float(instance.solute_std.quantity_stock) - float(instance.quantity_std), 2))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solute_std.id,
            type_transaction='Uso - Preparación Sln STD',
            date_transaction=timezone.localdate(),
            detail_transaction='Solución Estándar ' + instance.code_solution_std + ' al ' + str(
                instance.concentration_std) + instance.concentration_unit,
            quantity=instance.quantity_std,
            user_transaction_id=instance.user_creation.id,
        )

        # Registro de transacciones, uso de solvente
        if not instance.solute_std.reagent.ready_to_use:
            InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
                quantity_stock=round(instance.solvent_reagent.quantity_stock - instance.quantity_solvent, 2))

            TransactionReagent.objects.create(
                reagent_inventory_id=instance.solvent_reagent.id,
                type_transaction='Uso',
                date_transaction=timezone.localdate(),
                detail_transaction='Solución Estándar' + instance.code_solution_std + ' al ' + str(
                    instance.concentration_std) + instance.concentration_unit,
                quantity=instance.quantity_solvent,
                user_transaction_id=instance.user_creation.id,
            )


# Descuento de inventario de soluciones Estándares
@receiver(post_save, sender=StandardizationSolution)
def discount_inventory_std_solution(sender, instance, created, **kwargs):
    """
    Descontar inventario y registrar transacciones
    al crear una nueva estandarización de solución.
    """

    if not created:
        return

    # Usar transacción atómica para garantizar consistencia
    with transaction.atomic():

        # Actualizar estándar (solución estándar o reactivo pesado)
        if instance.standard_solution_id:
            std_solution = SolutionStd.objects.select_for_update().get(pk=instance.standard_solution_id)
            std_solution.quantity_available_std = round(
                float(std_solution.quantity_available_std) - float(instance.quantity_solution), 2
            )
            std_solution.save(update_fields=['quantity_available_std'])
        elif instance.standard_reagent_id:
            standard_reagent = InventoryReagent.objects.select_for_update().get(pk=instance.standard_reagent_id)
            InventoryReagent.objects.filter(pk=instance.standard_reagent_id).update(
                quantity_stock=round(
                    float(standard_reagent.quantity_stock) - float(instance.quantity_standard), 2
                )
            )

        # Actualizar Solution STD
        solution = SolutionStd.objects.select_for_update().get(pk=instance.solution_to_standardize_id)
        new_quantity = round(
            float(solution.quantity_available_std) - float(instance.quantity_standard), 2
        )
        SolutionStd.objects.filter(pk=instance.solution_to_standardize_id).update(quantity_available_std=new_quantity)

        current_time = timezone.now()
        detail_text = f'Estandarización de Solución {instance.solution_to_standardize.code_solution_std}'

        # Crear transacción del estándar utilizado
        if instance.standard_solution_id:
            TransactionSolutionStd.objects.create(
                solution_std_inventory_id=instance.standard_solution.id,
                type_transaction='Estandarización',
                date_transaction=current_time,
                detail_transaction=detail_text,
                quantity=instance.quantity_solution,
                user_transaction_id=instance.user_creation.id,
            )
        elif instance.standard_reagent_id:
            TransactionReagent.objects.create(
                reagent_inventory_id=instance.standard_reagent.id,
                type_transaction='Estandarización',
                date_transaction=current_time,
                detail_transaction=detail_text,
                quantity=instance.quantity_solution,
                user_transaction_id=instance.user_creation.id,
            )

        if instance.solution_to_standardize_id:
            TransactionSolutionStd.objects.create(
                solution_std_inventory_id=instance.solution_to_standardize.id,
                type_transaction='Estandarización',
                date_transaction=current_time,
                detail_transaction='Gasto en Estandarización',
                quantity=instance.quantity_standard,
                user_transaction_id=instance.user_creation.id,
            )

        # Calcular estadísticas de forma eficiente
        stats = StandardizationSolution.objects.filter(
            solution_to_standardize_id=instance.solution_to_standardize_id
        ).aggregate(
            average=Avg('concentration_sln'),
            deviation_std=StdDev('concentration_sln')
        )

        # Procesar estadísticas con validaciones robustas
        raw_average = stats.get('average')
        raw_deviation_std = stats.get('deviation_std')

        media = _round_solution_value(raw_average, instance.solution_to_standardize)
        standard_deviation = _round_solution_sig_figs(raw_deviation_std, 4)

        # Calcular RSD (Coeficiente de Variación) desde los valores crudos
        # None (no hay datos) y 0 (desviación nula) son distintos.
        rsd = None
        if raw_average and raw_average > 0:
            if raw_deviation_std == 0:
                rsd = _round_solution_value(Decimal('0'), instance.solution_to_standardize, decimals=2)
            elif raw_deviation_std is not None:
                rsd = _round_solution_value(
                    (raw_deviation_std / raw_average) * 100,
                    instance.solution_to_standardize, decimals=2)

        # Actualizar solución con estadísticas calculadas
        SolutionStd.objects.filter(pk=instance.solution_to_standardize_id).update(
            average_concentration=media,
            deviation_std=standard_deviation,
            coefficient_variation=rsd
        )


# Recalculo de Media de concentración, desviación estándar y RSD
@receiver(post_delete, sender=StandardizationSolution)
def recalculate_solution_stats_on_delete(sender, instance, **kwargs):
    """
    Signal para recalcular estadísticas de la solución cuando se elimina
    una estandarización. Actualiza promedio, desviación estándar y RSD.
    """
    # Sin solución asociada no hay estadísticas que recalcular
    if not instance.solution_to_standardize_id:
        return

    # En un borrado en cascada la solución padre ya no existe: no hay nada que actualizar
    solution = SolutionStd.objects.filter(pk=instance.solution_to_standardize_id).first()
    if solution is None:
        return

    with transaction.atomic():
        # Recalcular estadísticas con las estandarizaciones restantes
        stats = StandardizationSolution.objects.filter(
            solution_to_standardize_id=instance.solution_to_standardize_id
        ).aggregate(
            average=Avg('concentration_sln'),
            deviation_std=StdDev('concentration_sln')
        )

        # Procesar estadísticas
        raw_average = stats.get('average')
        raw_deviation_std = stats.get('deviation_std')

        media = _round_solution_value(raw_average, solution)
        standard_deviation = _round_solution_sig_figs(raw_deviation_std, 4)

        # Calcular RSD (Coeficiente de Variación) desde los valores crudos
        # None (no hay datos) y 0 (desviación nula) son distintos.
        rsd = None
        if raw_average and raw_average > 0:
            if raw_deviation_std == 0:
                rsd = _round_solution_value(Decimal('0'), solution, decimals=2)
            elif raw_deviation_std is not None:
                rsd = _round_solution_value(
                    (raw_deviation_std / raw_average) * 100, solution, decimals=2)

        # Actualizar solución con nuevas estadísticas
        # Si no quedan estandarizaciones, los valores serán None
        SolutionStd.objects.filter(pk=solution.pk).update(
            average_concentration=media,
            deviation_std=standard_deviation,
            coefficient_variation=rsd
        )


def _round_solution_value(value, solution_std=None, decimals=None):
    """
    Redondea un valor al número de decimales configurado en el SolutionStdBase
    de la solución, empleando Decimal para mayor precisión científica.

    El valor de ``sig_figs_solution`` se interpreta como número de decimales.
    Si es ``None``, vacío o ``0`` (o si la solución ya no existe), se usa 4.

    Args:
        value: Valor a redondear (puede ser None, float, Decimal, etc.)
        solution_std: Instancia de SolutionStd (puede ser None o estar borrada)
        decimals: Número de decimales explícito. Si es None se toma de
                  ``sig_figs_solution`` (default 4)

    Returns:
        Decimal redondeado o None si el valor es None/inválido
    """
    if value is None:
        return None

    if decimals is None:
        try:
            decimals = solution_std.solution_std_base.sig_figs_solution or 4
        except (AttributeError, ObjectDoesNotExist):
            decimals = 4

    try:
        decimals = int(decimals)
        if decimals <= 0:
            decimals = 4

        decimal_value = Decimal(str(value))
        quantize_exp = Decimal(10) ** -decimals
        return decimal_value.quantize(quantize_exp, rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, InvalidOperation):
        return None


def _round_solution_sig_figs(value, sig_figs=4):
    """
    Redondea un valor a cifras significativas reales empleando Decimal y
    ROUND_HALF_UP.

    Ejemplos: 0.015982 con 4 cifras -> 0.01598; 2.9866 con 4 cifras -> 2.987.

    Args:
        value: Valor a redondear (puede ser None, float, Decimal, etc.)
        sig_figs: Número de cifras significativas (default: 4)

    Returns:
        Decimal redondeado o None si el valor es None/inválido
    """
    if value is None:
        return None

    try:
        sig_figs = int(sig_figs) if sig_figs and int(sig_figs) > 0 else 4

        decimal_value = Decimal(str(value))
        if decimal_value == 0:
            return Decimal('0')

        decimals = sig_figs - 1 - decimal_value.adjusted()
        quantize_exp = Decimal(10) ** -decimals
        return decimal_value.quantize(quantize_exp, rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, InvalidOperation):
        return None
