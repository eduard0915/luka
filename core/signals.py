from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.db import transaction
from django.db.models import Avg, StdDev, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import InventoryReagent, TransactionReagent
from core.solution.models import Solution, SolutionStd, StandardizationSolution, TransactionSolution, \
    TransactionSolutionStd
from core.user.models import Training


# Registrar actualizado en capacitación
@receiver(post_save, sender=Training)
def update_training(sender, instance, **kwargs):
    # Solo procede si el estado es 'Vencido'
    if instance.training_status == 'Vencido':
        return

    training_last = Training.objects.filter(
        description_training=instance.description_training, user__slug=instance.user.slug).last()
    training_count = Training.objects.filter(
        description_training=instance.description_training, user__slug=instance.user.slug).count()
    if training_count > 1:
        Training.objects.filter(
            description_training=instance.description_training,
            pk=training_last.id, user__slug=instance.user.slug).update(training_status='Actualizado')


# Descuento de inventario de reactivos soluto para soluciones
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solute(sender, instance, created, **kwargs):
    if created:
        InventoryReagent.objects.filter(pk=instance.solute_reagent.id).update(
            quantity_stock=float(instance.solute_reagent.quantity_stock - instance.quantity_reagent))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solute_reagent.id,
            type_transaction='Uso',
            date_transaction=timezone.localtime(timezone.now()),
            detail_transaction='Solución ' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_reagent,
            user_transaction_id=instance.preparated_by.id,
        )


# Descuento de inventario de reactivos soluto para soluciones estándares
@receiver(post_save, sender=SolutionStd)
def discount_inventory_reagent_std(sender, instance, created, **kwargs):
    if created:
        InventoryReagent.objects.filter(pk=instance.solute_std.id).update(
            quantity_stock=float(instance.solute_std.quantity_stock - instance.quantity_std))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solute_std.id,
            type_transaction='Uso',
            date_transaction=timezone.localtime(timezone.now()),
            detail_transaction='Solución Estándar ' + instance.code_solution_std + ' al ' + str(
                instance.concentration_std) + instance.concentration_unit,
            quantity=instance.quantity_std,
            user_transaction_id=instance.preparated_std_by.id,
        )
        return


# Descuento de inventario de reactivos solvente en preparación de soluciones
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solvent(sender, instance, **kwargs):
    if instance.quantity_solvent and instance.solvent_reagent:
        InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
            quantity_stock=float(instance.solvent_reagent.quantity_stock - instance.quantity_solvent))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solvent_reagent.id,
            type_transaction='Uso',
            date_transaction=timezone.localtime(timezone.now()),
            detail_transaction='Solución ' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_solvent,
            user_transaction_id=instance.preparated_by.id,
        )
        return


# Descuento de inventario de reactivos solvente en preparación de soluciones Estándares
@receiver(post_save, sender=SolutionStd)
def discount_inventory_reagent_solvent_std(sender, instance, **kwargs):
    if instance.quantity_solvent and instance.solvent_reagent:
        InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
            quantity_stock=round(instance.solvent_reagent.quantity_stock - instance.quantity_solvent, 2))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solvent_reagent.id,
            type_transaction='Uso',
            date_transaction=timezone.localtime(timezone.now()),
            detail_transaction='Solución Estándar' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_solvent,
            user_transaction_id=instance.preparated_std_by.id,
        )
        return


# Registro de Transacción de ingreso de reactivo en inventario
@receiver(post_save, sender=InventoryReagent)
def register_inventory_reagent(sender, instance, created, **kwargs):

    if created:
        # Registro de ingreso de reactivo al inventario
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.id,
            type_transaction='Entrada',
            date_transaction=timezone.localtime(timezone.now()),
            detail_transaction='Ingreso de Reactivo a Inventario',
            quantity=instance.quantity_stock,
            user_transaction_id=instance.user_creation.id,
        )
        return

# Descuento de inventario de soluciones Estándares
# @receiver(post_save, sender=StandardizationSolution)
# def discount_inventory_std_solution(sender, instance, created, **kwargs):
#     """
#     Signal optimizado para descontar inventario y registrar transacciones
#     al crear una nueva estandarización de solución.
#     """
#     # Salida temprana si no es una creación
#     if not created:
#         return
#
#     # Usar transacción atómica para garantizar consistencia
#     with transaction.atomic():
#         # 1. Actualizar inventarios usando F() expressions y select_for_update()
#         # Esto previene race conditions y es más eficiente
#         SolutionStd.objects.select_for_update().filter(
#             pk=instance.standard_sln_id
#         ).update(
#             quantity_solution_std=F('quantity_solution_std') - Decimal(str(instance.quantity_standard))
#         )
#
#         Solution.objects.select_for_update().filter(
#             pk=instance.solution_id
#         ).update(
#             quantity_solution=F('quantity_solution') - Decimal(str(instance.quantity_aliquot))
#         )
#
#         # 2. Crear transacciones en bulk (más eficiente)
#         current_time = timezone.localtime(timezone.now())
#         detail_text = f'Estandarización de Solución {instance.solution.code_solution}'
#
#         transactions = [
#             TransactionSolution(
#                 solution_inventory_id=instance.solution_id,
#                 type_transaction='Uso - Estandarización',
#                 date_transaction=current_time,
#                 detail_transaction=detail_text,
#                 quantity=instance.quantity_aliquot,
#                 user_transaction_id=instance.standardized_by_id,
#             ),
#             TransactionSolutionStd(
#                 solution_std_inventory_id=instance.standard_sln_id,
#                 type_transaction='Uso - Estandarización',
#                 date_transaction=current_time,
#                 detail_transaction=detail_text,
#                 quantity=instance.quantity_standard,
#                 user_transaction_id=instance.standardized_by_id,
#             )
#         ]
#
#         # Nota: Si TransactionSolution y TransactionSolutionStd son modelos diferentes,
#         # se crean por separado. Si fueran el mismo modelo, usar bulk_create([...])
#         TransactionSolution.objects.create(**transactions[0].__dict__)
#         TransactionSolutionStd.objects.create(**transactions[1].__dict__)
#
#         # 3. Calcular estadísticas de forma eficiente
#         stats = StandardizationSolution.objects.filter(
#             solution_id=instance.solution_id
#         ).aggregate(
#             average=Avg('concentration_sln'),
#             deviation_std=StdDev('concentration_sln')
#         )
#
#         # 4. Procesar estadísticas con validaciones robustas
#         media = _round_decimal(stats.get('average'))
#         standard_deviation = _round_decimal(stats.get('deviation_std'))
#
#         # Calcular RSD (Coeficiente de Variación)
#         rsd = None
#         if media and standard_deviation and media > 0:
#             rsd = _round_decimal((standard_deviation / media) * Decimal('100'))
#
#         # 5. Actualizar solución con estadísticas calculadas
#         Solution.objects.filter(pk=instance.solution).update(
#             average_concentration=media,
#             deviation_std=standard_deviation,
#             coefficient_variation=rsd
#         )


@receiver(post_save, sender=StandardizationSolution)
def discount_inventory_std_solution(sender, instance, created, **kwargs):
    if not created:
        return
    # Disminución de inventario de solución STD por consumo
    SolutionStd.objects.filter(pk=instance.standard_sln.id).update(
        quantity_solution_std=round((instance.standard_sln.quantity_solution_std - instance.quantity_standard), 2))

    # Disminución de inventario de solución por estandarización
    Solution.objects.filter(pk=instance.solution.id).update(
        quantity_solution=round((instance.solution.quantity_solution - instance.quantity_aliquot), 2))

    # Registro de consumo de solución
    TransactionSolution.objects.create(
        solution_inventory_id=instance.solution.id,
        type_transaction='Uso - Estandarización',
        date_transaction=timezone.localtime(timezone.now()),
        detail_transaction='Estandarización de Solución ' + instance.solution.code_solution,
        quantity=instance.quantity_aliquot,
        user_transaction_id=instance.standardized_by.id,
    )

    # Registro de consumo de solución estándar
    TransactionSolutionStd.objects.create(
        solution_std_inventory_id=instance.standard_sln.id,
        type_transaction='Uso - Estandarización',
        date_transaction=timezone.localtime(timezone.now()),
        detail_transaction='Estandarización de Solución ' + instance.solution.code_solution,
        quantity=instance.quantity_standard,
        user_transaction_id=instance.standardized_by.id,
    )

    # Obtener promedio y desviación estándar
    stats = StandardizationSolution.objects.filter(solution=instance.solution).aggregate(
        average=Avg('concentration_sln'),
        deviation_std=StdDev('concentration_sln')
    )

    # Promedio y desviación estándar con redondeo a 4 decimales
    media = round(stats['average'], 4) if stats['average'] else None
    standard_deviation = round(stats['deviation_std'], 4) if stats['deviation_std'] else None

    # Cálculo de RSD (Coeficiente de Variación)
    if media and media != 0 and standard_deviation is not None:
        rsd = round((standard_deviation / media) * 100, 4)
    else:
        rsd = None

    # Guardado de Media de concentración, desviación estándar y coeficiente de variación
    Solution.objects.filter(pk=instance.solution.id).update(
        average_concentration=media, deviation_std=standard_deviation, coefficient_variation=rsd)


@receiver(post_delete, sender=StandardizationSolution)
def recalculate_solution_stats_on_delete(sender, instance, **kwargs):
    """
    Signal para recalcular estadísticas de la solución cuando se elimina
    una estandarización. Actualiza promedio, desviación estándar y RSD.
    """
    with transaction.atomic():
        # Recalcular estadísticas con las estandarizaciones restantes
        stats = StandardizationSolution.objects.filter(
            solution_id=instance.solution_id
        ).aggregate(
            average=Avg('concentration_sln'),
            deviation_std=StdDev('concentration_sln')
        )

        # Procesar estadísticas
        media = _round_decimal(stats.get('average'))
        standard_deviation = _round_decimal(stats.get('deviation_std'))

        # Calcular RSD (Coeficiente de Variación)
        rsd = None
        if media and standard_deviation and media > 0:
            rsd = _round_decimal((standard_deviation / media) * Decimal('100'))

        # Actualizar solución con nuevas estadísticas
        # Si no quedan estandarizaciones, los valores serán None
        Solution.objects.filter(pk=instance.solution_id).update(
            average_concentration=media,
            deviation_std=standard_deviation,
            coefficient_variation=rsd
        )


def _round_decimal(value, decimals=4):
    """
    Redondea un valor a un número específico de decimales usando Decimal.
    Más preciso que round() para operaciones financieras/científicas.

    Args:
        value: Valor a redondear (puede ser None, float, Decimal, etc.)
        decimals: Número de decimales (default: 4)

    Returns:
        Decimal redondeado o None si el valor es None/inválido
    """
    if value is None:
        return None

    try:
        decimal_value = Decimal(str(value))
        if decimal_value == 0:
            return Decimal('0')

        quantize_exp = Decimal(10) ** -decimals
        return decimal_value.quantize(quantize_exp, rounding=ROUND_HALF_UP)
    except (ValueError, TypeError, InvalidOperation):
        return None
