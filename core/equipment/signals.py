from django.db.models.signals import post_save
from django.dispatch import receiver
from core.equipment.models import Calibration, Maintenance

@receiver(post_save, sender=Calibration)
def update_previous_calibrations(sender, instance, created, **kwargs):
    """
    Cuando se crea o edita una calibración, busca instancias anteriores
    del mismo equipo y marca calibration_next_completed como True.
    """
    # Buscamos todas las calibraciones del mismo equipo, excluyendo la actual,
    # que todavía no estén marcadas como completadas.
    previous_calibrations = Calibration.objects.filter(
        equipment_instrumental=instance.equipment_instrumental,
        calibration_next_completed=False
    ).exclude(pk=instance.pk)
    
    # Marcamos las anteriores como completadas
    previous_calibrations.update(calibration_next_completed=True)


@receiver(post_save, sender=Maintenance)
def update_previous_maintenances(sender, instance, created, **kwargs):
    """
    Cuando se crea o edita un mantenimiento, busca instancias anteriores
    del mismo equipo y marca maintenance_next_completed como True.
    """
    # Buscamos todos los mantenimientos del mismo equipo, excluyendo el actual,
    # que todavía no estén marcados como completados.
    previous_maintenances = Maintenance.objects.filter(
        equipment_instrumental=instance.equipment_instrumental,
        maintenance_next_completed=False
    ).exclude(pk=instance.pk)

    # Marcamos los anteriores como completados
    previous_maintenances.update(maintenance_next_completed=True)
