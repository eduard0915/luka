from datetime import date
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog, SamplingProcess
from core.sampling.services import generate_samplings_for_group
from core.sampling.tests.factories import build_sampling_group


def run(*args, **kwargs):
    out = StringIO()
    call_command('generate_samplings', *args, stdout=out, stderr=out, **kwargs)
    return out.getvalue()


class GenerateSamplingsCommandTests(TestCase):
    def test_crea_las_muestras_del_dia(self):
        build_sampling_group(per_day=3)
        output = run(date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 3)
        self.assertIn('3 muestras creadas', output)

    def test_idempotente_correr_dos_veces(self):
        build_sampling_group(per_day=3)
        run(date='2026-07-16')
        run(date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 3)
        self.assertEqual(SamplingGenerationLog.objects.count(), 1)

    def test_catchup_de_dias_perdidos(self):
        group = build_sampling_group(per_day=2)
        run(date='2026-07-10')
        run(date='2026-07-13')  # 3 días sin correr
        dates = list(
            SamplingGenerationLog.objects.filter(sampling_group=group)
            .order_by('target_date')
            .values_list('target_date', flat=True)
        )
        self.assertEqual(dates, [date(2026, 7, 10), date(2026, 7, 11), date(2026, 7, 12), date(2026, 7, 13)])
        self.assertEqual(SamplingProcess.objects.count(), 8)

    def test_catchup_respeta_tope_de_30_dias(self):
        group = build_sampling_group(per_day=1)
        run(date='2026-01-01')
        run(date='2026-07-16')  # mucho más de 30 días después
        posteriores = SamplingGenerationLog.objects.filter(
            sampling_group=group, target_date__gt=date(2026, 1, 1)
        )
        self.assertEqual(posteriores.earliest('target_date').target_date, date(2026, 6, 16))
        self.assertEqual(posteriores.count(), 31)  # 2026-06-16 a 2026-07-16 inclusive

    def test_grupo_deshabilitado_sin_backfill_al_rehabilitar(self):
        group = build_sampling_group(per_day=2, enabled=False)
        run(date='2026-07-15')
        self.assertEqual(SamplingProcess.objects.count(), 0)
        self.assertTrue(
            SamplingGenerationLog.objects.get(sampling_group=group, target_date=date(2026, 7, 15)).skipped
        )

        group.enable_sampling_group = True
        group.save()
        run(date='2026-07-16')
        # Solo se genera el día actual; el período deshabilitado no se rellena
        self.assertEqual(SamplingProcess.objects.count(), 2)
        self.assertEqual(
            SamplingGenerationLog.objects.filter(sampling_group=group, skipped=False).count(), 1
        )

    def test_dry_run_no_escribe(self):
        build_sampling_group(per_day=3)
        output = run('--dry-run', date='2026-07-16')
        self.assertEqual(SamplingProcess.objects.count(), 0)
        self.assertEqual(SamplingGenerationLog.objects.count(), 0)
        self.assertIn('dry-run', output)

    def test_date_futura_es_rechazada(self):
        build_sampling_group(per_day=2)
        with self.assertRaises(CommandError):
            run(date='2099-01-01')
        self.assertEqual(SamplingGenerationLog.objects.count(), 0)

    def test_log_futuro_no_congela_el_dia_actual(self):
        group = build_sampling_group(per_day=2)
        SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 8, 16))
        run(date='2026-07-16')
        self.assertTrue(
            SamplingGenerationLog.objects.filter(sampling_group=group, target_date=date(2026, 7, 16)).exists()
        )
        self.assertEqual(SamplingProcess.objects.count(), 2)

    def test_error_en_un_grupo_no_bloquea_los_demas(self):
        malo = build_sampling_group(code='MAL', per_day=2)
        build_sampling_group(code='OK', per_day=2)

        real = generate_samplings_for_group

        def falla_solo_el_malo(group, target_date):
            if group.sampling_point.sample_point_code == 'MAL':
                raise RuntimeError('fallo simulado del grupo MAL')
            return real(group, target_date)

        with mock.patch(
            'core.sampling.management.commands.generate_samplings.generate_samplings_for_group',
            side_effect=falla_solo_el_malo,
        ):
            with self.assertRaises(CommandError):
                run(date='2026-07-16')

        creados = SamplingProcess.objects.filter(
            group_sampling__sampling_point__sample_point_code='OK'
        )
        self.assertEqual(creados.count(), 2)
        self.assertEqual(
            SamplingProcess.objects.filter(group_sampling=malo).count(), 0
        )
