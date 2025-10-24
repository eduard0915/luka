from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import InventoryReagent, TransactionReagent
from core.solution.models import Solution
from core.user.models import Training


# Registrar actualizado en capacitación
@receiver(post_save, sender=Training)
def update_training(sender, instance, **kwargs):
    # Solo procede si el estado es 'Vencido'
    if instance.training_status == 'Vencido':
        return

    training_last = Training.objects.filter(
        description_training=instance.description_training, user__slug=instance.user.slug).last()
    training_count = Training.objects.filter(description_training=instance.description_training).count()
    if training_count > 1:
        Training.objects.filter(description_training=instance.description_training, pk=training_last.id).update(training_status='Actualizado')


# Registro de Transacción de ingreso de reactivo en inventario
@receiver(post_save, sender=InventoryReagent)
def register_inventory_reagent(sender, instance, created, **kwargs):
    if created:
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.id,
            type_transaction='Entrada',
            date_transaction=timezone.now(),
            detail_transaction='Ingreso de Reactivo a Inventario',
            quantity=instance.quantity_stock,
        )
        return


# Descuento de inventario de reactivos solvente
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solvent(sender, instance, **kwargs):
    if instance.quantity_solvent:
        InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
            quantity_stock=float(instance.solvent_reagent.quantity_stock - instance.quantity_solvent))


# Descuento de inventario de reactivos soluto
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solute(sender, instance, **kwargs):
    if instance.quantity_solvent:
        InventoryReagent.objects.filter(pk=instance.solute_reagent.id).update(
            quantity_stock=float(instance.solute_reagent.quantity_stock - instance.quantity_reagent))
