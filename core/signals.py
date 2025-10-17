from django.db.models.signals import post_save
from django.dispatch import receiver

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