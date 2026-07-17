from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase

from core.sampling.models import SamplingGenerationLog
from core.sampling.tests.factories import build_sampling_group


class SamplingGenerationLogTests(TestCase):
    def test_defaults(self):
        group = build_sampling_group()
        log = SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        self.assertEqual(log.samples_created, 0)
        self.assertFalse(log.skipped)

    def test_unico_por_grupo_y_fecha(self):
        group = build_sampling_group()
        SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SamplingGenerationLog.objects.create(sampling_group=group, target_date=date(2026, 7, 16))
