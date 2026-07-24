"""Señales de Django para la aplicación de usuarios."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.user.models import Training


# Registrar actualizado en capacitación
@receiver(post_save, sender=Training)
def update_training(sender, instance, **kwargs):
    """Actualiza el estado de capacitaciones previas a 'Actualizado' cuando se registra una nueva del mismo tipo."""
    if instance.training_status == 'Vencido':
        return

    training_last = Training.objects.select_related('user').filter(
        description_training=instance.description_training, user__slug=instance.user.slug).last()
    training_count = Training.objects.select_related('user').filter(
        description_training=instance.description_training, user__slug=instance.user.slug).count()
    if training_count > 1:
        Training.objects.select_related('user').filter(
            description_training=instance.description_training,
            pk=training_last.id, user__slug=instance.user.slug).update(training_status='Actualizado')
