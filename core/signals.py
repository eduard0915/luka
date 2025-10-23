from django.db.models.signals import post_save
from django.dispatch import receiver

from core.reagent.models import InventoryReagent
from core.solution.models import Solution
from core.user.models import Training


# Signal para registrar actualizado en capacitación
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


# Signal para descuento de inventario de reactivos solvente
@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solvent(sender, instance, **kwargs):
    if instance.quantity_solvent:
        InventoryReagent.objects.filter(pk=instance.solvent_reagent.id).update(
            quantity_stock=float(instance.solvent_reagent.quantity_stock - instance.quantity_solvent))


@receiver(post_save, sender=Solution)
def discount_inventory_reagent_solute(sender, instance, **kwargs):
    if instance.quantity_solvent:
        InventoryReagent.objects.filter(pk=instance.solute_reagent.id).update(
            quantity_stock=float(instance.solute_reagent.quantity_stock - instance.quantity_reagent))
