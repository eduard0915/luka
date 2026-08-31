"""Pruebas para la generación del Certificado de Calidad (PDF) de procesos de muestreo."""

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.analytical_method.models import AnalyticalMethod
from core.laboratory.models import Laboratory
from core.sampling.models import SamplingAnalysis, SamplingProcess
from core.sampling.tests.factories import build_sample_point
from core.user.models import User


class SamplingProcessQualityCertificateTests(TestCase):
    """Pruebas para SamplingProcessQualityCertificatePDFView."""

    @classmethod
    def setUpTestData(cls):
        cls.point = build_sample_point(code='QC1')
        cls.site = cls.point.product.site
        cls.laboratory = Laboratory.objects.create(
            laboratory_name='Lab Test', site=cls.site
        )
        cls.user = User.objects.create_user(
            username='qc_analista', password='test1234', laboratory=cls.laboratory,
            first_name='Ana', last_name='Control'
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='add_reagent')
        )
        cls.method = AnalyticalMethod.objects.create(
            description_analytical_method='Titulación Ácido Base',
            code_analytical_method='TAB-01',
            sample_size=1.0,
            type_method='Volumetría',
            laboratory=cls.laboratory,
        )

        cls.sampling = SamplingProcess.objects.create(
            point_sampling=cls.point,
            type_sampling='En Proceso',
            date_sampling_scheduled=timezone.now(),
            date_sampling=timezone.now(),
            number_sample='QC1-20260101-1',
            batch_number='LOTE-001',
            status_sampling='Aprobado',
            sampling_created_by=cls.user,
            sampling_confirmed_by=cls.user,
            approved_by=cls.user,
        )

        cls.analysis = SamplingAnalysis.objects.create(
            sampling_process=cls.sampling,
            analytical_method=cls.method,
            average_concentration=0.98,
            standard_deviation=0.01,
            coefficient_variation=1.0,
            comply='Cumple',
            date_analysis=timezone.now(),
            verified_by=cls.user,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_pdf_generado_para_muestra_aprobada(self):
        """El certificado se descarga cuando la muestra está aprobada."""
        url = reverse('sampling:quality_certificate_pdf', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('certificado_calidad_', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_generado_para_muestra_rechazada(self):
        """El certificado se descarga cuando la muestra está rechazada."""
        self.sampling.status_sampling = 'Rechazado'
        self.sampling.save()
        url = reverse('sampling:quality_certificate_pdf', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_no_generado_para_muestra_en_proceso(self):
        """El certificado no se genera si la muestra no está aprobada o rechazada."""
        self.sampling.status_sampling = 'En Proceso'
        self.sampling.save()
        url = reverse('sampling:quality_certificate_pdf', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('sampling:detail_sampling_process', kwargs={'pk': self.sampling.pk})
        )

    def test_pdf_requiere_permiso(self):
        """El certificado requiere autenticación y permiso."""
        self.client.logout()
        url = reverse('sampling:quality_certificate_pdf', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_boton_certificado_visible_en_detalle_aprobado(self):
        """El botón de Certificado de Calidad se muestra cuando el estado es Aprobado."""
        url = reverse('sampling:detail_sampling_process', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertContains(response, '/sampling/process/certificate/')
        self.assertContains(response, 'Certificado de Calidad')

    def test_boton_certificado_no_visible_en_detalle_en_proceso(self):
        """El botón de Certificado de Calidad no se muestra en estados intermedios."""
        self.sampling.status_sampling = 'En Proceso'
        self.sampling.save()
        url = reverse('sampling:detail_sampling_process', kwargs={'pk': self.sampling.pk})
        response = self.client.get(url)
        self.assertNotContains(response, '/sampling/process/certificate/')
