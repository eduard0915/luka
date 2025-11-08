from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.reagent.models import InventoryReagent, TransactionReagent
from core.solution.models import Solution, SolutionStd
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
            date_transaction=timezone.now(),
            detail_transaction='Solución ' + instance.code_solution + ' al ' + str(
                instance.concentration) + instance.concentration_unit,
            quantity=instance.quantity_reagent,
            user_transaction_id=instance.preparated_by.id,
        )
        return


# Descuento de inventario de reactivos soluto para soluciones estándares
@receiver(post_save, sender=SolutionStd)
def discount_inventory_reagent_std(sender, instance, created, **kwargs):
    if created:
        InventoryReagent.objects.filter(pk=instance.solute_std.id).update(
            quantity_stock=float(instance.solute_std.quantity_stock - instance.quantity_std))

        TransactionReagent.objects.create(
            reagent_inventory_id=instance.solute_std.id,
            type_transaction='Uso',
            date_transaction=timezone.now(),
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
            date_transaction=timezone.now(),
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
            date_transaction=timezone.now(),
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
        TransactionReagent.objects.create(
            reagent_inventory_id=instance.id,
            type_transaction='Entrada',
            date_transaction=timezone.now(),
            detail_transaction='Ingreso de Reactivo a Inventario',
            quantity=instance.quantity_stock,
            user_transaction_id=instance.user_creation.id,
        )
        return
