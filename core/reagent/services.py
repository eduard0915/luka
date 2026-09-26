"""Servicios de negocio para el módulo de reactivos.

Contiene la lógica de ajuste del stock de inventario al registrar, editar
o eliminar el uso de un reactivo en un análisis de muestra.
"""

from django.db import transaction

from core.reagent.models import InventoryReagent


def register_transaction_reagent(transaction_reagent):
    """Descuenta del inventario la cantidad usada por una transacción de reactivo."""
    with transaction.atomic():
        inventory = InventoryReagent.objects.select_for_update().get(
            pk=transaction_reagent.reagent_inventory_id)
        inventory.quantity_stock = (inventory.quantity_stock or 0) - (transaction_reagent.quantity or 0)
        inventory.save(update_fields=['quantity_stock'])
    return inventory


def update_transaction_reagent_stock(transaction_reagent, previous_quantity, previous_inventory_id):
    """Ajusta el inventario al editar: devuelve la cantidad anterior y descuenta la nueva."""
    with transaction.atomic():
        inventory_ids = {previous_inventory_id, transaction_reagent.reagent_inventory_id}
        locked_inventories = {
            inventory.pk: inventory
            for inventory in InventoryReagent.objects.select_for_update().filter(pk__in=inventory_ids)
        }

        previous_inventory = locked_inventories.get(previous_inventory_id)
        if previous_inventory is not None:
            previous_inventory.quantity_stock = (previous_inventory.quantity_stock or 0) + (previous_quantity or 0)
            previous_inventory.save(update_fields=['quantity_stock'])

        new_inventory = locked_inventories.get(transaction_reagent.reagent_inventory_id)
        if new_inventory is not None:
            new_inventory.quantity_stock = (new_inventory.quantity_stock or 0) - (transaction_reagent.quantity or 0)
            new_inventory.save(update_fields=['quantity_stock'])
    return new_inventory


def delete_transaction_reagent_stock(transaction_reagent):
    """Devuelve al inventario la cantidad usada por una transacción eliminada."""
    with transaction.atomic():
        inventory = InventoryReagent.objects.select_for_update().get(
            pk=transaction_reagent.reagent_inventory_id)
        inventory.quantity_stock = (inventory.quantity_stock or 0) + (transaction_reagent.quantity or 0)
        inventory.save(update_fields=['quantity_stock'])
    return inventory
