"""Pruebas unitarias para los formularios de la aplicación sampling."""

from django.contrib.auth.models import Permission
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from crum import impersonate

from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculate
from core.laboratory.models import Laboratory
from core.sampling.forms import (
    SamplingAnalysisProcessingGravimetryForm, SamplingGroupForm, SamplingProcessForm,
)
from core.sampling.models import SamplingAnalysis, SamplingProcess
from core.sampling.tests.factories import build_sample_point, build_sampling_group
from core.user.models import User
from core.utils import round_sig_figs


def build_gravimetry_setup(sig_figs_result=4, code='GRA-01'):
    """Crea analista, método gravimétrico y análisis con la configuración de Materia Insoluble Total."""
    point = build_sample_point(code='GRAP')
    laboratory = Laboratory.objects.create(laboratory_name='Lab Gravimetría', site=point.product.site)
    user = User.objects.create_user(
        username='analista-grav', password='test1234', laboratory=laboratory,
    )
    user.user_permissions.add(Permission.objects.get(codename='add_reagent'))

    method = AnalyticalMethod.objects.create(
        description_analytical_method='Materia Insoluble Total',
        code_analytical_method=code,
        sample_size=100.0,
        type_method='Gravimetrico',
        laboratory=laboratory,
        sig_figs_result=sig_figs_result,
    )
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, calculate_description='% de Insolubles Totales')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, position='Numerador', gross_weight='Peso Filtro + Residuo')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, position='Numerador', weight_of_filter='Peso Filtro')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, position='Numerador', factor=100.0)

    sampling = SamplingProcess.objects.create(
        point_sampling=point,
        type_sampling='Producto Terminado',
        date_sampling_scheduled=timezone.now(),
        number_sample='GRAP-20260101-1',
    )
    analysis = SamplingAnalysis.objects.create(sampling_process=sampling, analytical_method=method)
    return user, method, analysis


class SamplingProcessFormTests(TestCase):
    """Pruebas para el formulario de procesos de muestreo."""
    def test_sin_grupo_ni_punto_es_invalido(self):
        """Verifica que el formulario es inválido cuando no se selecciona grupo ni punto de muestreo."""
        form = SamplingProcessForm(data={
            'type_sampling': 'En Proceso',
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Debe seleccionar un Grupo de Muestreo o un Punto de Muestreo.',
            form.non_field_errors(),
        )

    def test_con_grupo_es_valido(self):
        """Verifica que el formulario es válido al seleccionar un grupo de muestreo."""
        group = build_sampling_group()
        form = SamplingProcessForm(data={
            'type_sampling': 'En Proceso',
            'group_sampling': group.pk,
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_con_solo_punto_es_valido(self):
        """Verifica que el formulario es válido al seleccionar solo un punto de muestreo."""
        point = build_sample_point(code='PT1', sample_type='Producto Terminado')
        form = SamplingProcessForm(data={
            'type_sampling': 'Producto Terminado',
            'point_sampling': point.pk,
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['point_sampling'], point)
        self.assertIsNone(form.cleaned_data['group_sampling'])

    def test_con_grupo_y_punto_gana_el_grupo(self):
        """Verifica que al enviar grupo y punto, el grupo prevalece y el punto se limpia (regresión)."""
        # Regresión: con dos `if` independientes quedaban AMBOS en None y la muestra
        # se guardaba sin origen, reventando en generate_sample_code().
        group = build_sampling_group()
        point = build_sample_point(code='PT2', sample_type='Producto Terminado')
        form = SamplingProcessForm(data={
            'type_sampling': 'En Proceso',
            'group_sampling': group.pk,
            'point_sampling': point.pk,
            'date_sampling_scheduled': '2026-07-16 08:00',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['group_sampling'], group)
        self.assertIsNone(form.cleaned_data['point_sampling'])


class SamplingGroupFormTests(TestCase):
    """Pruebas para el formulario de grupos de muestreo."""
    def test_solo_ofrece_puntos_diarios(self):
        """Verifica que el formulario solo muestra puntos con periodicidad diaria en el campo sampling_point."""
        diario = build_sample_point(code='DIA', sample_frequency=6, periodicity='Diaria')
        legacy = build_sample_point(code='LEG', sample_frequency=6, periodicity='Diario')
        semanal = build_sample_point(code='SEM', sample_frequency=6, periodicity='Semanal')

        queryset = SamplingGroupForm().fields['sampling_point'].queryset
        self.assertIn(diario, queryset)
        self.assertIn(legacy, queryset)
        self.assertNotIn(semanal, queryset)

    def test_grupo_legacy_no_diario_sigue_siendo_editable(self):
        """Verifica que un grupo con periodicidad no diaria aún se puede editar (regresión)."""
        # Regresión: el filtro por periodicidad dejaba la pantalla de edición rota
        # ('Escoja una opción válida') para grupos creados antes de la feature.
        semanal = build_sample_point(code='SEM', sample_frequency=6, periodicity='Semanal')
        grupo = build_sampling_group(point=semanal, per_day=4)
        form = SamplingGroupForm(
            data={'sampling_point': str(semanal.pk), 'first_hour_sampling': '08:00',
                  'number_sampling_day': '4'},
            instance=grupo,
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_no_se_puede_crear_grupo_nuevo_sobre_punto_no_diario(self):
        """Verifica que no se permite crear un grupo nuevo sobre un punto con periodicidad no diaria."""
        semanal = build_sample_point(code='SEM2', sample_frequency=6, periodicity='Semanal')
        form = SamplingGroupForm(
            data={'sampling_point': str(semanal.pk), 'first_hour_sampling': '08:00',
                  'number_sampling_day': '4'})
        self.assertFalse(form.is_valid())
        self.assertIn('sampling_point', form.errors)


class RoundSigFigsTests(SimpleTestCase):
    """Pruebas del helper de redondeo por cifras significativas."""
    def test_redondea_por_cifras_significativas_no_por_decimales(self):
        """Valores pequeños conservan sus cifras significativas en lugar de redondearse a 0.0."""
        self.assertEqual(round_sig_figs(0.003, 2), 0.003)
        self.assertEqual(round_sig_figs(0.003333, 2), 0.0033)
        self.assertEqual(round_sig_figs(0.003333, 4), 0.003333)
        self.assertEqual(round_sig_figs(0.00123, 2), 0.0012)

    def test_valores_grandes_redondean_a_la_izquierda(self):
        """Valores grandes redondean las cifras a la izquierda del punto decimal."""
        self.assertEqual(round_sig_figs(1234.5, 2), 1200.0)
        self.assertEqual(round_sig_figs(1234.5, 3), 1230.0)
        self.assertEqual(round_sig_figs(1.0, 4), 1.0)

    def test_cero_y_sig_figs_invalido(self):
        """El cero retorna 0.0 y un número de cifras inválido usa el default 4."""
        self.assertEqual(round_sig_figs(0, 2), 0.0)
        self.assertEqual(round_sig_figs(0.0, None), 0.0)
        self.assertEqual(round_sig_figs(0.123456, None), 0.1235)
        self.assertEqual(round_sig_figs(0.123456, 0), 0.1235)


class SamplingAnalysisProcessingGravimetryFormTests(TestCase):
    """Pruebas para el cálculo de la concentración en el formulario gravimétrico."""

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.method, cls.analysis = build_gravimetry_setup()

    def _save(self, weight_obtained, weight_of_filter, quantity_sample, analysis=None):
        form = SamplingAnalysisProcessingGravimetryForm(
            data={
                'weight_obtained': weight_obtained,
                'weight_of_filter': weight_of_filter,
                'quantity_sample': quantity_sample,
            },
            analysis=analysis or self.analysis,
        )
        self.assertTrue(form.is_valid(), form.errors)
        with impersonate(self.user):
            return form.save()

    def test_peso_bruto_y_peso_filtro_marcan_el_peso_neto(self):
        """Regresión: guardaba 1.0 porque ignoraba las filas de peso bruto/peso filtro."""
        # Caso real del método 'Materia Insoluble Total': (1.115 - 1.112) * 100 / 100 = 0.003
        instance = self._save(1.115, 1.112, 100.0)
        self.assertAlmostEqual(instance.concentration_sample, 0.003, places=6)

        self.analysis.refresh_from_db()
        self.assertAlmostEqual(self.analysis.average_concentration, 0.003, places=6)

    def test_variable_marca_el_peso_neto(self):
        """Métodos que marcan el peso neto con 'variable' siguen calculando igual."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Sólidos Disueltos',
            code_analytical_method='GRA-02',
            sample_size=100.0,
            type_method='Gravimetrico',
            laboratory=self.method.laboratory,
            sig_figs_result=4,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', variable='Peso Neto')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=100.0)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        instance = self._save(1.115, 1.112, 100.0, analysis=analysis)
        self.assertAlmostEqual(instance.concentration_sample, 0.003, places=6)

    def test_valor_pequeno_no_se_redondea_a_cero(self):
        """Regresión: con 2 cifras significativas 0.00123 se redondeaba a 0.0."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Residuo Seco',
            code_analytical_method='GRA-03',
            sample_size=100.0,
            type_method='Gravimetrico',
            laboratory=self.method.laboratory,
            sig_figs_result=2,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', gross_weight='Peso Cápsula + Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', weight_of_filter='Peso Cápsula')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=100.0)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        # (1.00123 - 1.0) * 100 / 100 = 0.00123 -> 2 cifras significativas = 0.0012
        instance = self._save(1.00123, 1.0, 100.0, analysis=analysis)
        self.assertAlmostEqual(instance.concentration_sample, 0.0012, places=6)

    def test_cantidad_de_muestra_cero_guarda_cero(self):
        """Sin cantidad de muestra la concentración se guarda en cero."""
        instance = self._save(1.115, 1.112, 0.0)
        self.assertEqual(instance.concentration_sample, 0)


class SamplingAnalysisDetailEquationTests(TestCase):
    """Pruebas de la ecuación del método mostrada en el detalle del análisis."""

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.method, cls.analysis = build_gravimetry_setup()

    def test_detalle_muestra_ecuacion_gravimetrica(self):
        """El detalle muestra la ecuación con peso bruto, peso filtro y peso de muestra."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[self.analysis.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Peso Filtro + Residuo')
        self.assertContains(response, 'Peso Filtro')
        self.assertContains(response, 'Peso de Muestra')
        self.assertContains(response, '100.0')

    def test_detalle_muestra_ecuacion_volumetrica(self):
        """Los métodos no gravimétricos muestran sus términos en numerador y denominador."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Acidez Total',
            code_analytical_method='VOL-01',
            sample_size=20.0,
            type_method='Volumetrico',
            laboratory=self.method.laboratory,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Acidez',
            unit_measure_calculate='%')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', volumen_std='mL Estándar')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=0.1)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='mL Muestra')
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[analysis.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'mL Estándar')
        self.assertContains(response, 'mL Muestra')
