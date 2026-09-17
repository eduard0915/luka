"""Comando de administración para la generación automática de muestras."""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone

from core.company.models import Company
from core.sampling.models import SamplingGenerationLog, SamplingGroup
from core.sampling.services import (
    compute_sampling_times,
    generate_samplings_for_group,
    should_skip_group,
)

CATCHUP_MAX_DAYS = 30


class Command(BaseCommand):
    """Comando que crea las muestras programadas del día para cada grupo de muestreo."""
    help = 'Crea las muestras programadas (SamplingProcess) del día para cada grupo de muestreo, con recuperación de días perdidos'

    def add_arguments(self, parser):
        """Configura los argumentos opcionales del comando."""
        parser.add_argument('--date', help="Simula la fecha de 'hoy' (YYYY-MM-DD); para pruebas y operación manual")
        parser.add_argument('--dry-run', action='store_true', help='Reporta lo que se crearía sin escribir en la base de datos')

    def handle(self, *args, **options):
        """Ejecuta la generación de muestras para todos los grupos habilitados."""
        if options['date']:
            today = datetime.strptime(options['date'], '%Y-%m-%d').date()
            # Un log con fecha futura congelaría al grupo: el catch-up avanza desde
            # el último log y no rellena huecos intermedios.
            if today > timezone.localdate():
                raise CommandError('--date no puede ser una fecha futura')
        else:
            today = timezone.localdate()
        dry_run = options['dry_run']

        total_created = 0
        days_generated = 0
        errors = 0

        # Solo genera si hay al menos una compañía con autosample y service_software activos
        if not Company.objects.filter(autosample=True, service_software=True).exists():
            self.stdout.write('No hay compañías habilitadas para automuestreo')
            return

        groups = SamplingGroup.objects.filter(
            enable_sampling_group=True, enable_sampling_auto=True
        ).select_related('sampling_point').order_by('date_creation')

        for group in groups:
            try:
                created, days = self._process_group(group, today, dry_run)
                total_created += created
                days_generated += days
            except Exception as exc:
                errors += 1
                self.stderr.write(f'ERROR en grupo {group.id} ({group}): {exc}')

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(
            f'{prefix}{total_created} muestras creadas, {days_generated} días generados, {errors} grupos con error'
        )
        if errors:
            raise CommandError(f'{errors} grupos con error')

    def _process_group(self, group, today, dry_run):
        """Procesa un grupo de muestreo generando las muestras desde el último registro hasta hoy."""
        last = SamplingGenerationLog.objects.filter(
            sampling_group=group, target_date__lte=today,   # ignora logs de días futuros
        ).aggregate(last=Max('target_date'))['last']
        start = last + timedelta(days=1) if last else today
        floor = today - timedelta(days=CATCHUP_MAX_DAYS)
        if start < floor:
            start = floor

        created = 0
        days = 0
        day = start
        while day <= today:
            if dry_run:
                if should_skip_group(group):
                    self.stdout.write(f'[dry-run] {group}: omitido para {day}')
                else:
                    times = compute_sampling_times(group, day)
                    self.stdout.write(f'[dry-run] {group}: {len(times)} muestras para {day}')
                    days += 1
                    created += len(times)
            else:
                log = generate_samplings_for_group(group, day)
                if log is not None and not log.skipped:
                    days += 1
                    created += log.samples_created
            day += timedelta(days=1)
        return created, days
