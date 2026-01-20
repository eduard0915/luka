from crum import get_current_user
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import TransactionReagent, InventoryReagent


# Registro de Transacción de ingreso de reactivo en inventario
@receiver(post_save, sender=InventoryReagent)
def register_inventory_reagent(sender, instance, created, **kwargs):

    if not created:
        return

    # Evitar ejecución durante fixtures/migraciones
    if kwargs.get('raw', False):
        return

    # Registro de ingreso de reactivo al inventario
    if instance.quantity_stock > 0:
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.id,
            type_transaction='Entrada',
            date_transaction=timezone.localdate(),
            detail_transaction='Ingreso de Reactivo a Inventario',
            quantity=instance.quantity_stock,
            user_transaction=instance.user_creation,
        )
