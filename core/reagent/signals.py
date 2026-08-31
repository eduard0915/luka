"""Señales de Django para la aplicación de reactivos.

Registra automáticamente las transacciones de entrada cuando se crea un
nuevo registro de inventario de reactivo.
"""

from crum import get_current_user
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import TransactionReagent, InventoryReagent


@receiver(post_save, sender=InventoryReagent)
def register_inventory_reagent(sender, instance, created, **kwargs):
    """Crea una transacción de entrada automática al registrar un nuevo inventario de reactivo."""
    if not created:
        return

    if kwargs.get('raw', False):
        return

    if instance.quantity_stock > 0:
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.id,
            type_transaction='Entrada',
            date_transaction=timezone.localdate(),
            detail_transaction='Ingreso de Reactivo a Inventario',
            quantity=instance.quantity_stock,
            user_transaction=instance.user_creation,
        )
