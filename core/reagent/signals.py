from crum import get_current_user
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import TransactionReagent, InventoryReagent
from core.solution.models import SolutionStd, code_solution_std_generator, TransactionSolutionStd


# Registro de Transacción de ingreso de reactivo en inventario
@receiver(post_save, sender=InventoryReagent)
def register_inventory_reagent(sender, instance, created, **kwargs):

    if not created:
        return

    # Evitar ejecución durante fixtures/migraciones
    if kwargs.get('raw', False):
        return

    # Registro de ingreso de reactivo al inventario
    TransactionReagent.objects.create(
        reagent_inventory_id=instance.id,
        type_transaction='Entrada',
        date_transaction=timezone.localdate(),
        detail_transaction='Ingreso de Reactivo a Inventario',
        quantity=instance.quantity_stock,
        user_transaction=instance.user_creation,
    )

    if instance.reagent.ready_to_use:
        solution = SolutionStd(
            solute_std=instance,
            code_solution_std=code_solution_std_generator(),
            concentration_std=instance.purity,
            concentration_unit=instance.reagent.purity_unit,
            expire_std_date_solution=instance.date_expire,
            quantity_solution_std=instance.quantity_stock,
            quantity_std=0,
            quantity_solvent=0,
            preparation_confirmed=True,
            user_creation=instance.user_creation,
        )
        solution.save()

        std = TransactionSolutionStd(
            solution_std_inventory=instance,
            date_transaction=timezone.localdate(),
            type_transaction='Entrada',
            detail_transaction='Ingreso a Inventario de Soluciones Estándares',
            quantity=instance.quantity_stock,
            user_transaction=instance.user_creation,
        )
        std.save()
