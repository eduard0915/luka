"""Pruebas unitarias para los servicios de generación de muestras."""

from datetime import date, time, timedelta
from unittest import mock

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from core.sampling.models import SamplingGenerationLog, SamplingProcess
from core.sampling.services import compute_sampling_times, generate_samplings_for_group
from core.sampling.tests.factories import build_sample_point, build_sampling_group

TARGET = date(2026, 7, 16)


class ComputeSamplingTimesTests(TestCase):
    """Pruebas para la función compute_sampling_times."""
    def test_distribucion_uniforme_con_cruce_de_medianoche(self):
        """Verifica que los horarios se distribuyen uniformemente incluso cruzando la medianoche."""
        group = build_sampling_group(first_hour='07:00:00', per_day=4)
        times = [timezone.localtime(t) for t in compute_sampling_times(group, TARGET)]
        self.assertEqual(
            [(t.date(), t.time()) for t in times],
            [
                (TARGET, time(7, 0)),
                (TARGET, time(13, 0)),
                (TARGET, time(19, 0)),
                (TARGET + timedelta(days=1), time(1, 0)),
            ],
        )

    def test_intervalo_coincide_con_la_frecuencia_del_punto(self):
        """Verifica que el intervalo entre muestras coincide con la frecuencia configurada en el punto."""
        # Matriz real de FREQUENCY (core/product/forms.py): N = floor(24/f), todos divisores de 24
        for frecuencia, per_day in [(4, 6), (6, 4), (8, 3), (12, 2), (24, 1)]:
            with self.subTest(frecuencia=frecuencia):
                group = build_sampling_group(first_hour='07:00:00', per_day=per_day)
                times = compute_sampling_times(group, TARGET)
                self.assertEqual(len(times), per_day)
                if per_day > 1:
                    self.assertEqual(times[1] - times[0], timedelta(hours=frecuencia))

    def test_intervalo_para_frecuencia_de_8_horas(self):
        """Verifica que 3 muestras por día generan intervalos de 8 horas comenzando a las 07:00."""
        group = build_sampling_group(first_hour='07:00:00', per_day=3)  # 24h / 8h = 3
        times = [timezone.localtime(t).time() for t in compute_sampling_times(group, TARGET)]
        self.assertEqual(times, [time(7, 0), time(15, 0), time(23, 0)])

    def test_todos_los_horarios_son_aware(self):
        """Verifica que todos los horarios generados tienen zona horaria (timezone-aware)."""
        group = build_sampling_group(per_day=3)
        for t in compute_sampling_times(group, TARGET):
            self.assertFalse(timezone.is_naive(t))


class GenerateSamplingsForGroupTests(TestCase):
    """Pruebas para la función generate_samplings_for_group."""
    def test_crea_lote_completo_con_campos_correctos(self):
        """Verifica que generate_samplings_for_group crea el lote completo con todos los campos correctos."""
        group = build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4)
        log = generate_samplings_for_group(group, TARGET)

        self.assertEqual(log.samples_created, 4)
        self.assertFalse(log.skipped)
        samples = SamplingProcess.objects.filter(group_sampling=group).order_by('date_sampling_scheduled')
        self.assertEqual(samples.count(), 4)

        first = samples.first()
        self.assertEqual(first.type_sampling, 'En Proceso')
        self.assertTrue(first.automatic_sampling)
        self.assertEqual(first.status_sampling, 'Programada')
        self.assertIsNone(first.user_creation)
        self.assertEqual(first.number_sample, 'PM1-20260716-1')
        # La muestra que cruza a día siguiente conserva la fecha del lote en su código
        self.assertEqual(samples.last().number_sample, 'PM1-20260716-4')

        # La UI debe mostrar la hora local del spec (07:00), no UTC
        first.refresh_from_db()
        self.assertEqual(first.toJSON()['date_sampling_scheduled'], '2026-07-16 07:00:00')

    def test_idempotente(self):
        """Verifica que llamar dos veces generate_samplings_for_group no duplica las muestras."""
        group = build_sampling_group(per_day=4)
        self.assertIsNotNone(generate_samplings_for_group(group, TARGET))
        self.assertIsNone(generate_samplings_for_group(group, TARGET))
        self.assertEqual(SamplingProcess.objects.count(), 4)
        self.assertEqual(SamplingGenerationLog.objects.count(), 1)

    def test_grupo_deshabilitado_se_omite(self):
        """Verifica que un grupo con enable_sampling_group=False se omite y se marca como skipped."""
        group = build_sampling_group(enabled=False)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(log.samples_created, 0)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_punto_deshabilitado_se_omite(self):
        """Verifica que un punto con enable_point=False causa que el grupo se omita."""
        point = build_sample_point(code='PM1', enable_point=False)
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_punto_sin_codigo_se_omite(self):
        """Verifica que un punto sin código de muestreo causa que el grupo se omita."""
        point = build_sample_point(code='')
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_punto_legacy_diario_si_genera(self):
        """Verifica que un punto con periodicidad 'Diario' (legacy) sí genera muestras."""
        point = build_sample_point(code='PM1', periodicity='Diario', sample_frequency=6)  # default histórico del modelo
        group = build_sampling_group(point=point, per_day=4)
        log = generate_samplings_for_group(group, TARGET)
        self.assertFalse(log.skipped)
        self.assertEqual(log.samples_created, 4)

    def test_punto_no_diario_se_omite(self):
        """Verifica que un punto con periodicidad no diaria (ej. Semanal) causa que el grupo se omita."""
        point = build_sample_point(code='PM1', periodicity='Semanal')
        group = build_sampling_group(point=point)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_grupo_con_cero_muestras_por_dia_se_omite(self):
        """Verifica que un grupo con number_sampling_day=0 se omite y se marca como skipped."""
        group = build_sampling_group(per_day=0)
        log = generate_samplings_for_group(group, TARGET)
        self.assertTrue(log.skipped)
        self.assertEqual(SamplingProcess.objects.count(), 0)

    def test_integrityerror_ajeno_al_constraint_no_se_silencia(self):
        """Verifica que IntegrityError no relacionado con unicidad no se silencia (regresión)."""
        # Regresión: el except atrapaba CUALQUIER IntegrityError y devolvía None, que el
        # comando interpreta como 'ya generado' -> el lote se perdía y el cron reportaba éxito.
        group = build_sampling_group(per_day=3)
        with mock.patch.object(
            SamplingProcess.objects, 'create',
            side_effect=IntegrityError('violación de FK'),
        ):
            with self.assertRaises(IntegrityError):
                generate_samplings_for_group(group, TARGET)
        self.assertEqual(SamplingGenerationLog.objects.count(), 0)
