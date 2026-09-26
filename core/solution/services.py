"""Servicios de negocio para el módulo de soluciones.

Contiene la lógica de transferencia de reactivos del inventario
a soluciones estándar listas para usar.
"""

from django.db import transaction
from django.utils import timezone
from core.reagent.models import TransactionReagent
from core.solution.models import Solution, SolutionStd, code_solution_std_generator, TransactionSolutionStd

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


def register_transaction_solution(transaction_solution):
    """Descuenta del inventario la cantidad usada por una transacción de solución."""
    with transaction.atomic():
        solution = Solution.objects.select_for_update().get(pk=transaction_solution.solution_inventory_id)
        solution.quantity_available_sln = (solution.quantity_available_sln or 0) - (transaction_solution.quantity or 0)
        solution.save(update_fields=['quantity_available_sln'])
    return solution


def update_transaction_solution_stock(transaction_solution, previous_quantity, previous_solution_id):
    """Ajusta el inventario al editar: devuelve la cantidad anterior y descuenta la nueva."""
    with transaction.atomic():
        solution_ids = {previous_solution_id, transaction_solution.solution_inventory_id}
        locked_solutions = {
            solution.pk: solution
            for solution in Solution.objects.select_for_update().filter(pk__in=solution_ids)
        }

        previous_solution = locked_solutions.get(previous_solution_id)
        if previous_solution is not None:
            previous_solution.quantity_available_sln = (previous_solution.quantity_available_sln or 0) + (previous_quantity or 0)
            previous_solution.save(update_fields=['quantity_available_sln'])

        new_solution = locked_solutions.get(transaction_solution.solution_inventory_id)
        if new_solution is not None:
            new_solution.quantity_available_sln = (new_solution.quantity_available_sln or 0) - (transaction_solution.quantity or 0)
            new_solution.save(update_fields=['quantity_available_sln'])
    return new_solution


def delete_transaction_solution_stock(transaction_solution):
    """Devuelve al inventario la cantidad usada por una transacción eliminada."""
    with transaction.atomic():
        solution = Solution.objects.select_for_update().get(pk=transaction_solution.solution_inventory_id)
        solution.quantity_available_sln = (solution.quantity_available_sln or 0) + (transaction_solution.quantity or 0)
        solution.save(update_fields=['quantity_available_sln'])
    return solution
