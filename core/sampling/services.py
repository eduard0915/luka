from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingProcess, next_sample_number

# Periodicidades que esta feature programa. 'Diario' (masculino) es el default
# histórico del modelo (core/product/models.py) y cuenta como diario; las choices
# de la UI usan 'Diaria' (core/product/forms.py).
DAILY_PERIODICITY = {'Diaria', 'Diario'}


# Horarios del día: intervalo uniforme de 24h / number_sampling_day desde first_hour_sampling.
# Los horarios que cruzan medianoche caen en target_date + 1 pero pertenecen al lote de target_date.
def compute_sampling_times(group, target_date):
    interval = timedelta(hours=24) / group.number_sampling_day
    first = timezone.make_aware(
        datetime.combine(target_date, group.first_hour_sampling),
        timezone.get_current_timezone(),
    )
    return [first + k * interval for k in range(group.number_sampling_day)]


# Regla "sin punto de muestreo no hay muestras": el grupo debe estar habilitado,
# con al menos una muestra por día, y su punto habilitado, con código y diario.
def should_skip_group(group):
    point = group.sampling_point
    return (
        not group.enable_sampling_group
        or group.number_sampling_day < 1
        or not point.enable_point
        or not point.sample_point_code
        or point.periodicity not in DAILY_PERIODICITY
    )


# Crea el lote de muestras de un grupo para un día. Devuelve el log creado,
# o None si ese día ya estaba generado (constraint único grupo+fecha).
def generate_samplings_for_group(group, target_date):
    try:
        with transaction.atomic():
            log = SamplingGenerationLog.objects.create(
                sampling_group=group,
                target_date=target_date,
                skipped=should_skip_group(group),
            )
            if log.skipped:
                return log
            point = group.sampling_point
            for scheduled_at in compute_sampling_times(group, target_date):
                SamplingProcess.objects.create(
                    group_sampling=group,
                    type_sampling='En Proceso',
                    date_sampling_scheduled=scheduled_at,
                    automatic_sampling=True,
                    number_sample=next_sample_number(point, target_date),
                )
                log.samples_created += 1
            log.save(update_fields=['samples_created'])
            return log
    except IntegrityError:
        # Solo el choque con unique_group_target_date significa 'ya generado'.
        # Cualquier otra violación (FK a un grupo borrado, NOT NULL, ...) es un error
        # real: debe escalar al comando, que la cuenta y termina con CommandError.
        if SamplingGenerationLog.objects.filter(
            sampling_group=group, target_date=target_date
        ).exists():
            return None
        raise
