from django.db import transaction
from django.utils import timezone
from core.reagent.models import TransactionReagent
from core.solution.models import SolutionStd, code_solution_std_generator, TransactionSolutionStd

def transfer_inventory_reagent_to_std(inventory_reagent_id, solution_std_base, user):
    """
    Realiza el traslado de un InventoryReagent a una SolutionStd.
    """
    from core.reagent.models import InventoryReagent
    with transaction.atomic():
        inventory_reagent = InventoryReagent.objects.select_for_update().get(id=inventory_reagent_id)
        if inventory_reagent.quantity_stock <= 0:
            raise ValueError("No hay stock disponible para trasladar.")

        quantity_to_transfer = inventory_reagent.quantity_stock

        # 1. Crear instancia de SolutionStd
        solution_std = SolutionStd.objects.create(
            solute_std=inventory_reagent,
            solution_std_base=solution_std_base,
            code_solution_std=code_solution_std_generator(),
            concentration_std=inventory_reagent.purity,
            concentration_unit=inventory_reagent.reagent.purity_unit,
            expire_std_date_solution=inventory_reagent.date_expire,
            quantity_solution_std=quantity_to_transfer,
            quantity_std=0,
            quantity_solvent=0,
            preparation_confirmed=True,
            user_creation=user,
        )

        # 2. Registrar TransactionReagent de Traslado
        TransactionReagent.objects.create(
            reagent_inventory=inventory_reagent,
            type_transaction='Traslado',
            date_transaction=timezone.localdate(),
            detail_transaction=f'Traslado a Solución Estándar: {solution_std.code_solution_std}',
            quantity=quantity_to_transfer,
            user_transaction=user,
        )

        # 3. Registrar TransactionSolutionStd de Entrada
        TransactionSolutionStd.objects.create(
            solution_std_inventory=solution_std,
            date_transaction=timezone.localdate(),
            type_transaction='Entrada',
            detail_transaction=f'Ingreso por traslado desde Inventario de Reactivos: {inventory_reagent.reagent.code_reagent}',
            quantity=quantity_to_transfer,
            user_transaction=user,
        )

        # 4. Poner quantity_stock en 0
        inventory_reagent.quantity_stock = 0
        inventory_reagent.save()

    return solution_std
