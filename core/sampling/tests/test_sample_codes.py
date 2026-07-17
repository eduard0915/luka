from datetime import date

from django.test import TestCase
from django.utils import timezone

from core.product.models import SamplePoint
from core.sampling.models import SamplingProcess, next_sample_number
from core.sampling.tests.factories import build_sample_point


def create_sample(point, number=''):
    return SamplingProcess.objects.create(
        point_sampling=point,
        type_sampling='En Proceso',
        date_sampling_scheduled=timezone.now(),
        number_sample=number,
    )


class NextSampleNumberTests(TestCase):
    def test_secuencia_independiente_por_punto(self):
        # Regresión: intercalar puntos no debe reiniciar ni duplicar la secuencia
        point_a = build_sample_point(code='A')
        point_b = build_sample_point(code='B')
        today_str = timezone.localdate().strftime('%Y%m%d')

        sample_a1 = create_sample(point_a)
        sample_b1 = create_sample(point_b)
        sample_a2 = create_sample(point_a)

        self.assertEqual(sample_a1.number_sample, f'A-{today_str}-1')
        self.assertEqual(sample_b1.number_sample, f'B-{today_str}-1')
        self.assertEqual(sample_a2.number_sample, f'A-{today_str}-2')

    def test_fecha_explicita_para_catchup(self):
        point = build_sample_point(code='PM1')
        self.assertEqual(next_sample_number(point, date(2026, 7, 14)), 'PM1-20260714-1')

    def test_secuencia_continua_con_codigos_existentes(self):
        point = build_sample_point(code='PM1')
        create_sample(point, number='PM1-20260714-1')
        create_sample(point, number='PM1-20260714-2')
        self.assertEqual(next_sample_number(point, date(2026, 7, 14)), 'PM1-20260714-3')

    def test_sin_grupo_ni_punto_lanza_error(self):
        with self.assertRaises(ValueError):
            SamplingProcess.objects.create(
                type_sampling='En Proceso',
                date_sampling_scheduled=timezone.now(),
            )

    def test_codigo_largo_no_desborda_number_sample(self):
        # Regresión: sample_point_code admite 30 chars y el código completo debe caber.
        code = 'PUNTO-MUESTREO-LARGO-123456789'  # 30 chars = máximo de sample_point_code
        point = build_sample_point(code=code)
        sample = create_sample(point)
        today_str = timezone.localdate().strftime('%Y%m%d')
        self.assertEqual(sample.number_sample, f'{code}-{today_str}-1')

    def test_puntos_distintos_con_el_mismo_codigo_comparten_secuencia(self):
        # sample_point_code no es único: dos puntos de productos distintos pueden usar
        # 'PM1'. Compartir el contador es lo que evita códigos duplicados entre ellos.
        point_a = build_sample_point(code='PM1')
        point_b = build_sample_point(code='PM1')
        today_str = timezone.localdate().strftime('%Y%m%d')

        self.assertEqual(create_sample(point_a).number_sample, f'PM1-{today_str}-1')
        self.assertEqual(create_sample(point_b).number_sample, f'PM1-{today_str}-2')

    def test_codigo_prefijo_de_otro_no_colisiona(self):
        # 'PM1' es prefijo de 'PM10': el separador y la fecha deben evitar el falso match.
        point_1 = build_sample_point(code='PM1')
        point_10 = build_sample_point(code='PM10')
        today_str = timezone.localdate().strftime('%Y%m%d')

        create_sample(point_10)
        create_sample(point_10)
        self.assertEqual(create_sample(point_1).number_sample, f'PM1-{today_str}-1')

    def test_number_sample_cubre_el_maximo_de_sample_point_code(self):
        # Ata el acoplamiento entre los dos campos: {code}-{AAAAMMDD}-{n} => code_max + 1 + 8 + 1 + 5
        code_max = SamplePoint._meta.get_field('sample_point_code').max_length
        number_max = SamplingProcess._meta.get_field('number_sample').max_length
        self.assertGreaterEqual(number_max, code_max + 15)
