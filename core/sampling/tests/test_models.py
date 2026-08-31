"""Pruebas unitarias para los modelos de la aplicación sampling."""

from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog
from core.sampling.tests.factories import build_sampling_group


class SamplingGenerationLogTests(TestCase):
    """Pruebas para el modelo de registro de generación de muestras."""
    def test_defaults(self):
        """Verifica que los valores por defecto de SamplingGenerationLog son cero muestras y no omitido."""
        group = build_sampling_group()
        log = SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        self.assertEqual(log.samples_created, 0)
        self.assertFalse(log.skipped)

    def test_unico_por_grupo_y_fecha(self):
        """Verifica que la restricción único por grupo y fecha genera IntegrityError al duplicar."""
        group = build_sampling_group()
        SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
