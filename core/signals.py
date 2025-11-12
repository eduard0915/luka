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

    training_last = Training.objects.select_related('user').filter(
        description_training=instance.description_training, user__slug=instance.user.slug).last()
    training_count = Training.objects.select_related('user').filter(
        description_training=instance.description_training, user__slug=instance.user.slug).count()
    if training_count > 1:
        Training.objects.select_related('user').filter(
            description_training=instance.description_training,
            pk=training_last.id, user__slug=instance.user.slug).update(training_status='Actualizado')


# Descuento de inventario de reactivos soluto para soluciones
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solute(sender, instance, created, **kwargs):
    if not created:
        return
    InventoryReagent.objects.filter(pk=instance.solute_reagent.id).update(
        quantity_stock=round(float(instance.solute_reagent.quantity_stock) - float(instance.quantity_reagent), 2))

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
    if not created:
        return
    InventoryReagent.objects.filter(pk=instance.solute_std.id).update(
        quantity_stock=round(float(instance.solute_std.quantity_stock) - float(instance.quantity_std), 2))

    TransactionReagent.objects.create(
        reagent_inventory_id=instance.solute_std.id,
        type_transaction='Uso',
        date_transaction=timezone.localtime(timezone.now()),
        detail_transaction='Solución Estándar ' + instance.code_solution_std + ' al ' + str(
            instance.concentration_std) + instance.concentration_unit,
        quantity=instance.quantity_std,
        user_transaction_id=instance.preparated_std_by.id,
    )


# Descuento de inventario de reactivos solvente en preparación de soluciones
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solvent(sender, instance, created, **kwargs):
    """
    Descuenta inventario y crea transacción cuando se registra quantity_solvent.
    Solo se ejecuta cuando quantity_solvent tiene un valor nuevo.
    """
    # Validar que existan los datos necesarios
    if not (instance.quantity_solvent and instance.solvent_reagent_id):
        return

    # Si es actualización, verificar si quantity_solvent cambió
    if not created:
        # Obtener el valor anterior de quantity_solvent
        try:
            old_instance = Solution.objects.get(pk=instance.pk)
            # Si ya tenía un valor, no procesar (evitar duplicados)
            if old_instance.quantity_solvent:
                return
        except Solution.DoesNotExist:
            return

    # Usar transacción atómica para garantizar consistencia
    with transaction.atomic():
        # Actualizar inventario usando F() para evitar race conditions
        # y select_for_update para bloquear el registro
        InventoryReagent.objects.select_for_update().filter(
            pk=instance.solvent_reagent_id
        ).update(
            quantity_stock=F('quantity_stock') - instance.quantity_solvent
        )

        # Crear la transacción
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solvent_reagent_id,
            type_transaction='Uso',
            date_transaction=timezone.now(),  # Simplificado
            detail_transaction=(
                f'Solución {instance.code_solution} al '
                f'{instance.concentration}{instance.concentration_unit}'
            ),
            quantity=instance.quantity_solvent,
            user_transaction_id=instance.preparated_by_id,
        )
# @receiver(post_save, sender=Solution)
# def discount_inventory_reagent_solvent(sender, instance, **kwargs):
#     if instance.quantity_solvent and instance.solvent_reagent:
#         InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
#             quantity_stock=float(instance.solvent_reagent.quantity_stock - instance.quantity_solvent))
#
#         TransactionReagent.objects.create(
#             reagent_inventory_id=instance.solvent_reagent.id,
#             type_transaction='Uso',
#             date_transaction=timezone.localtime(timezone.now()),
#             detail_transaction='Solución ' + instance.code_solution + ' al ' + str(
#                 instance.concentration) + instance.concentration_unit,
#             quantity=instance.quantity_solvent,
#             user_transaction_id=instance.preparated_by.id,
#         )
#         return


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

    if not created:
        return
    # Registro de ingreso de reactivo al inventario
    TransactionReagent.objects.create(
        reagent_inventory_id=instance.id,
        type_transaction='Entrada',
        date_transaction=timezone.localtime(timezone.now()),
        detail_transaction='Ingreso de Reactivo a Inventario',
        quantity=instance.quantity_stock,
        user_transaction_id=instance.user_creation.id,
    )

# Descuento de inventario de soluciones Estándares
@receiver(post_save, sender=StandardizationSolution)
def discount_inventory_std_solution(sender, instance, created, **kwargs):
    """
    Signal optimizado para descontar inventario y registrar transacciones
    al crear una nueva estandarización de solución.
    """
    # Salida temprana si no es una creación
    if not created:
        return

    # Usar transacción atómica para garantizar consistencia
    with transaction.atomic():
        # 1. Actualizar inventarios de forma eficiente
        # Usamos refresh_from_db para obtener valores actuales y luego actualizamos
        # Esto es más simple y evita problemas de tipos de datos

        # Actualizar SolutionStd
        std_solution = SolutionStd.objects.select_for_update().get(pk=instance.standard_sln_id)
        std_solution.quantity_solution_std = round(
            float(std_solution.quantity_solution_std) - float(instance.quantity_standard), 2
        )
        std_solution.save(update_fields=['quantity_solution_std'])

        # Actualizar Solution
        solution = Solution.objects.select_for_update().get(pk=instance.solution_id)
        solution.quantity_solution = round(
            float(solution.quantity_solution) - float(instance.quantity_aliquot), 2
        )
        solution.save(update_fields=['quantity_solution'])

        # 2. Crear transacciones (modelos diferentes requieren creación separada)
        current_time = timezone.localtime(timezone.now())
        detail_text = f'Estandarización de Solución {instance.solution.code_solution}'

        # Crear transacción de solución
        TransactionSolution.objects.create(
            solution_inventory_id=instance.solution_id,
            type_transaction='Uso - Estandarización',
            date_transaction=current_time,
            detail_transaction=detail_text,
            quantity=instance.quantity_aliquot,
            user_transaction_id=instance.standardized_by_id,
        )

        # Crear transacción de solución estándar
        TransactionSolutionStd.objects.create(
            solution_std_inventory_id=instance.standard_sln_id,
            type_transaction='Uso - Estandarización',
            date_transaction=current_time,
            detail_transaction=detail_text,
            quantity=instance.quantity_standard,
            user_transaction_id=instance.standardized_by_id,
        )

        # 3. Calcular estadísticas de forma eficiente
        stats = StandardizationSolution.objects.filter(
            solution_id=instance.solution_id
        ).aggregate(
            average=Avg('concentration_sln'),
            deviation_std=StdDev('concentration_sln')
        )

        # 4. Procesar estadísticas con validaciones robustas
        media = _round_decimal(stats.get('average'))
        standard_deviation = _round_decimal(stats.get('deviation_std'))

        # Calcular RSD (Coeficiente de Variación)
        rsd = None
        if media and standard_deviation and media > 0:
            rsd = _round_decimal((standard_deviation / media) * Decimal('100'))

        # 5. Actualizar solución con estadísticas calculadas
        Solution.objects.filter(pk=instance.solution_id).update(
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
