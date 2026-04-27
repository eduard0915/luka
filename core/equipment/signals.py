from django.db.models.signals import post_save
from django.dispatch import receiver
from core.equipment.models import Calibration

@receiver(post_save, sender=Calibration)
def update_previous_calibrations(sender, instance, created, **kwargs):
    """
    Cuando se crea o edita una calibración, busca instancias anteriores
    del mismo equipo y marca calibration_next_completed como True.
    """
    previous_calibrations = Calibration.objects.filter(
        equipment_instrumental=instance.equipment_instrumental,
        calibration_next_completed=False
    ).exclude(pk=instance.pk)
    
    # Marcamos las anteriores como completadas
    previous_calibrations.update(calibration_next_completed=True)
