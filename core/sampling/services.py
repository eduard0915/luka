"""Lógica de negocio para la generación automática de muestras."""

from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingProcess, next_sample_number

DAILY_PERIODICITY = {'Diaria', 'Diario'}


def compute_sampling_times(group, target_date):
    """Calcula los horarios de muestreo distribuidos uniformemente en 24 horas."""
    interval = timedelta(hours=24) / group.number_sampling_day
    first = timezone.make_aware(
        datetime.combine(target_date, group.first_hour_sampling),
        timezone.get_current_timezone(),
    )
    return [first + k * interval for k in range(group.number_sampling_day)]


def should_skip_group(group):
    """Determina si un grupo de muestreo debe omitirse por no cumplir las condiciones."""
    point = group.sampling_point
    return (
        not group.enable_sampling_group
        or group.number_sampling_day < 1
        or not point.enable_point
        or not point.sample_point_code
        or point.periodicity not in DAILY_PERIODICITY
    )


def generate_samplings_for_group(group, target_date):
    """Crea el lote de muestras de un grupo para un día. Retorna el log o None si ya existía."""
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
