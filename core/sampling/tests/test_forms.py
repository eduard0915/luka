"""Pruebas unitarias para los formularios de la aplicación sampling."""

from django.contrib.auth.models import Permission
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from crum import impersonate

from core.analytical_method.models import (
    AnalyticalMethod, AnalyticalMethodCalculate, AnalyticalMethodSolutionStd, GravimetryTerm,
)
from core.laboratory.models import Laboratory
from core.product.models import AnalyticalMethodProduct, SpecificationProduct
from core.reagent.models import InventoryReagent, Reagent
from core.sampling.forms import (
    SamplingAnalysisProcessingForm, SamplingAnalysisProcessingGravimetryForm,
    SamplingAnalysisProcessingSpectrophotometryForm, SamplingGroupForm,
    SamplingProcessForm,
)
from core.sampling.models import SamplingAnalysis, SamplingAnalysisProcessing, SamplingProcess
from core.sampling.tests.factories import build_sample_point, build_sampling_group
from core.solution.models import SolutionStd, SolutionStdBase
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


def build_volumetry_setup(sig_figs_result=4, code='VOL-09', concentration_std=0.1, suffix='1'):
    """Crea analista, solución estándar, método volumétrico y análisis para pruebas de V_Total y V_2."""
    point = build_sample_point(code=f'VOLP{suffix}')
    laboratory = Laboratory.objects.create(
        laboratory_name=f'Lab Volumetría {suffix}', site=point.product.site)
    user = User.objects.create_user(
        username=f'analista-vol{suffix}', password='test1234', laboratory=laboratory,
    )
    user.user_permissions.add(Permission.objects.get(codename='add_reagent'))

    with impersonate(user):
        reagent = Reagent.objects.create(
            description_reagent='HCl Estándar', code_reagent=f'R-HCL-STD{suffix}', umb='mL',
            purity_unit='%', molecular_weight=36.46, gram_equivalent=36.46,
            site=point.product.site,
        )
        inventory = InventoryReagent.objects.create(
            reagent=reagent, batch_number=f'L-HCL-{suffix}', quantity_stock=1000.0, purity=0.1,
        )
        std_base = SolutionStdBase.objects.create(
            solute_std_base=reagent, concentration_std_base=concentration_std,
            concentration_unit_base='N',
        )
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Acidez Total',
            code_analytical_method=code,
            sample_size=20.0,
            type_method='Volumetrico',
            laboratory=laboratory,
            sig_figs_result=sig_figs_result,
        )
        AnalyticalMethodSolutionStd.objects.create(analytical_method=method, solution_std=std_base)
        solution_std = SolutionStd.objects.create(
            solute_std=inventory,
            solution_std_base=std_base,
            concentration_std=concentration_std,
            concentration_unit='N',
            quantity_solution_std=1000.0,
            quantity_available_std=1000.0,
            quantity_std=0.0,
            preparation_confirmed=True,
            laboratory=laboratory,
        )

    sampling = SamplingProcess.objects.create(
        point_sampling=point,
        type_sampling='Producto Terminado',
        date_sampling_scheduled=timezone.now(),
        number_sample=f'VOLP{suffix}-20260101-1',
    )
    analysis = SamplingAnalysis.objects.create(sampling_process=sampling, analytical_method=method)
    return user, method, analysis, solution_std


def build_spectrophotometry_setup(sig_figs_result=4, code='ESP-01', with_sample=True, suffix='1'):
    """Crea analista, método espectrofotométrico y análisis con absorbancia, muestra, constante y término."""
    point = build_sample_point(code=f'ESPP{suffix}')
    laboratory = Laboratory.objects.create(
        laboratory_name=f'Lab Espectrofotometría {suffix}', site=point.product.site)
    user = User.objects.create_user(
        username=f'analista-esp{suffix}', password='test1234', laboratory=laboratory,
    )
    user.user_permissions.add(Permission.objects.get(codename='add_reagent'))

    method = AnalyticalMethod.objects.create(
        description_analytical_method='Fósforo Total',
        code_analytical_method=code,
        sample_size=20.0,
        type_method='Espectrofotometrico',
        laboratory=laboratory,
        sig_figs_result=sig_figs_result,
    )
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, calculate_description='Concentración',
        unit_measure_calculate='mg/L')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, absorbance='Absorbancia', position='Numerador')
    if with_sample:
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, sample_quantity='Gramos de Muestra', position='Denominador')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, factor=2.5, position='Numerador')
    AnalyticalMethodCalculate.objects.create(
        analytical_method=method, factor=100, term_type='constant',
        operation='multiply', consecutive=2)

    sampling = SamplingProcess.objects.create(
        point_sampling=point,
        type_sampling='Producto Terminado',
        date_sampling_scheduled=timezone.now(),
        number_sample=f'ESPP{suffix}-20260101-1',
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

    def test_ecuacion_con_terminos_resta_el_calculo_basico(self):
        """La ecuación con términos evalúa '100 - cálculo básico' para la concentración."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Insolubles con Términos',
            code_analytical_method='GRA-04',
            sample_size=100.0,
            type_method='Gravimetrico',
            laboratory=self.method.laboratory,
            sig_figs_result=4,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', gross_weight='Peso Filtro + Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', weight_of_filter='Peso Filtro')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=100.0)
        GravimetryTerm.objects.create(
            analytical_method=method, term_type='constant', constant_value=100, consecutive=1)
        GravimetryTerm.objects.create(
            analytical_method=method, term_type='basic', operation='subtract', consecutive=2)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        # Cálculo básico = (2.0 - 1.0) * 100 / 100 = 1.0 -> 100 - 1.0 = 99.0
        instance = self._save(2.0, 1.0, 100.0, analysis=analysis)
        self.assertAlmostEqual(instance.concentration_sample, 99.0, places=6)

    def test_ecuacion_con_terminos_en_analytical_method_calculate(self):
        """Los términos guardados en AnalyticalMethodCalculate también evalúan la ecuación."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Insolubles con Términos',
            code_analytical_method='GRA-06',
            sample_size=100.0,
            type_method='Gravimetrico',
            laboratory=self.method.laboratory,
            sig_figs_result=4,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', gross_weight='Peso Filtro + Residuo',
            term_type='basic', operation='subtract', consecutive=2)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', weight_of_filter='Peso Filtro',
            term_type='basic', operation='subtract', consecutive=2)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra',
            term_type='basic', operation='subtract', consecutive=2)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=100.0)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, factor=100.0, term_type='constant', consecutive=1)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        # Cálculo básico = (2.0 - 1.0) * 100 / 100 = 1.0 -> 100 - 1.0 = 99.0
        instance = self._save(2.0, 1.0, 100.0, analysis=analysis)
        self.assertAlmostEqual(instance.concentration_sample, 99.0, places=6)


class SamplingAnalysisProcessingVolumetryFormTests(TestCase):
    """Pruebas del cálculo de concentración en el formulario volumétrico con V_Total y V_2."""

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.method, cls.analysis, cls.solution_std = build_volumetry_setup(sig_figs_result=5)
        # Ecuación: ((V_Total - V_2) × Factor) / (Alícuota × mL Muestra)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, calculate_description='Acidez', unit_measure_calculate='%')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, position='Numerador', volumen_std='V_Total')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, position='Numerador', volumen_std='V_2', operation='subtract')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, position='Numerador', factor=6.08)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, position='Denominador', aliquot=True)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=cls.method, position='Denominador', sample_quantity='mL Muestra')

    def test_vtotal_menos_v2_con_factor_alicuota_y_muestra(self):
        """Registra V_Total y V_2 como quantity_standard/quantity_standard_two y calcula la concentración.

        Datos: quantity_standard=19 (V_Total), quantity_standard_two=17 (V_2),
        factor=6.08, alícuota=5, muestra=1.5.
        Numerador: (19 - 17) × 6.08 = 12.16; Denominador: 5 × 1.5 = 7.5 → 1.6213
        """
        with impersonate(self.user):
            form = SamplingAnalysisProcessingForm(data={
                'standard_solution': self.solution_std.pk,
                'quantity_standard': 19,
                'quantity_standard_two': 17,
                'quantity_sample': 1.5,
                'aliquot': 5,
            }, analysis=self.analysis)
            self.assertTrue(form.is_valid(), form.errors)
            instance = form.save()

        self.assertEqual(instance.quantity_standard, 19)
        self.assertEqual(instance.quantity_standard_two, 17)
        self.assertEqual(instance.aliquot, 5)
        self.assertAlmostEqual(float(instance.concentration_sample), 1.6213, places=4)

        self.analysis.refresh_from_db()
        self.assertAlmostEqual(float(self.analysis.average_concentration), 1.6213, places=4)

    def test_volumetrico_dos_volumenes_con_concentracion_resta_por_defecto(self):
        """Caso real 'Determinación de Magnesio': dos volúmenes con solución estándar y sin operación.

        El segundo volumen resta del primero por defecto (V_Total - V_2), igual que la
        ecuación mostrada en el detalle, y la concentración del estándar aplica una vez:
        (19 - 17) × 0.0538 × 6.08 / (1.5 × 5) = 0.0872
        """
        user, method, analysis, solution_std = build_volumetry_setup(
            sig_figs_result=3, code='VOL-10', concentration_std=0.0538, suffix='2')
        std_base = solution_std.solution_std_base
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Determinacion de Mg')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Gramos de Muestra')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', volumen_std='mL Gastados',
            sln_std_base=std_base)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', volumen_std='mL Gastados',
            sln_std_base=std_base)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=6.08)
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', aliquot=True)

        with impersonate(user):
            form = SamplingAnalysisProcessingForm(data={
                'standard_solution': solution_std.pk,
                'quantity_standard': 19,
                'quantity_standard_two': 17,
                'quantity_sample': 1.5,
                'aliquot': 5,
            }, analysis=analysis)
            self.assertTrue(form.is_valid(), form.errors)
            instance = form.save()

        # Numerador: (19×0.0538 - 17×0.0538) × 6.08 = 0.6542; Denominador: 1.5 × 5 = 7.5
        self.assertAlmostEqual(float(instance.concentration_sample), 0.0872, places=4)

    def test_alicuota_y_v2_son_obligatorios_cuando_la_ecuacion_los_incluye(self):
        """El formulario exige alícuota y mL Estándar 2 cuando la ecuación los contiene."""
        with impersonate(self.user):
            form = SamplingAnalysisProcessingForm(data={
                'standard_solution': self.solution_std.pk,
                'quantity_standard': 19,
                'quantity_sample': 1.5,
            }, analysis=self.analysis)
        self.assertFalse(form.is_valid())
        self.assertIn('aliquot', form.errors)
        self.assertIn('quantity_standard_two', form.errors)


class SamplingAnalysisProcessingSpectrophotometryFormTests(TestCase):
    """Pruebas para el cálculo de la concentración en el formulario espectrofotométrico."""

    @classmethod
    def setUpTestData(cls):
        cls.user, cls.method, cls.analysis = build_spectrophotometry_setup()

    def _save(self, absorbance, quantity_sample=None, analysis=None):
        """Guarda el formulario espectrofotométrico con los valores indicados."""
        form = SamplingAnalysisProcessingSpectrophotometryForm(
            data={'absorbance': absorbance, 'quantity_sample': quantity_sample},
            analysis=analysis or self.analysis,
        )
        self.assertTrue(form.is_valid(), form.errors)
        with impersonate(self.user):
            return form.save()

    def _add_specification(self, lower, upper):
        """Crea la especificación del producto y la asocia al punto de muestreo."""
        point = self.analysis.sampling_process.point_sampling
        method_product = AnalyticalMethodProduct.objects.create(
            product=point.product, analytical_method=self.method)
        spec = SpecificationProduct.objects.create(
            product=point.product, type_test='Químico', test_prod='Fósforo Total',
            method_test=method_product, lower_limit_prod=lower, upper_limit_prod=upper,
            unit_measure='mg/L')
        point.specification.add(spec)
        return spec

    def test_calculo_con_absorbancia_muestra_constante_y_termino(self):
        """La concentración sigue la ecuación: (Absorbancia × 2.5 / Muestra) × 100."""
        instance = self._save(absorbance=0.5, quantity_sample=10.0)

        self.assertAlmostEqual(instance.concentration_sample, 12.5, places=6)

        self.analysis.refresh_from_db()
        self.assertAlmostEqual(self.analysis.average_concentration, 12.5, places=6)

    def test_metodo_sin_cantidad_de_muestra_no_la_exige(self):
        """Sin fila de muestra en la ecuación la cantidad de muestra no es obligatoria."""
        user, method, analysis = build_spectrophotometry_setup(
            code='ESP-02', with_sample=False, suffix='2')

        form = SamplingAnalysisProcessingSpectrophotometryForm(
            data={'absorbance': 0.5}, analysis=analysis)
        self.assertTrue(form.is_valid(), form.errors)
        with impersonate(user):
            instance = form.save()

        # Absorbancia × 2.5 × 100 = 125.0
        self.assertAlmostEqual(instance.concentration_sample, 125.0, places=6)

    def test_absorbancia_es_obligatoria(self):
        """Sin lectura de absorbancia el formulario es inválido."""
        form = SamplingAnalysisProcessingSpectrophotometryForm(
            data={'absorbance': '', 'quantity_sample': 10.0}, analysis=self.analysis)

        self.assertFalse(form.is_valid())
        self.assertIn('absorbance', form.errors)

    def test_comply_cumple_dentro_de_limites(self):
        """El concepto del análisis es 'Cumple' cuando el resultado está dentro de los límites."""
        self._add_specification(lower=1.0, upper=20.0)

        self._save(absorbance=0.5, quantity_sample=10.0)

        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.comply, 'Cumple')

    def test_comply_no_cumple_fuera_de_limites(self):
        """El concepto del análisis es 'No Cumple' cuando el resultado supera el límite."""
        self._add_specification(lower=1.0, upper=20.0)

        # (1.0 × 2.5 / 0.1) × 100 = 2500.0
        self._save(absorbance=1.0, quantity_sample=0.1)

        self.analysis.refresh_from_db()
        self.assertEqual(self.analysis.comply, 'No Cumple')

    def test_comply_con_especificacion_del_producto_sin_punto(self):
        """El concepto se evalúa con la especificación del producto aunque no esté en el punto."""
        point = self.analysis.sampling_process.point_sampling
        method_product = AnalyticalMethodProduct.objects.create(
            product=point.product, analytical_method=self.method)
        SpecificationProduct.objects.create(
            product=point.product, type_test='Químico', test_prod='Fósforo Total',
            method_test=method_product, lower_limit_prod=1.0, upper_limit_prod=20.0,
            unit_measure='mg/L')

        self._save(absorbance=0.5, quantity_sample=10.0)

        self.analysis.refresh_from_db()
        self.assertAlmostEqual(self.analysis.average_concentration, 12.5, places=6)
        self.assertEqual(self.analysis.comply, 'Cumple')

    def test_detalle_muestra_datos_del_procesamiento(self):
        """El detalle muestra la absorbancia, la muestra, el resultado y el concepto."""
        self._add_specification(lower=1.0, upper=20.0)
        self._save(absorbance=0.5, quantity_sample=10.0)

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[self.analysis.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Absorbancia')
        self.assertContains(response, 'Gramos de Muestra')
        self.assertContains(response, '0,5')
        self.assertContains(response, '10,0')
        self.assertContains(response, '12,5')
        self.assertContains(response, 'Cumple')

    def test_detalle_url_procesamiento_espectrofotometrico(self):
        """El detalle del análisis ofrece la URL de procesamiento espectrofotométrico."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[self.analysis.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['create_processing_url'],
            reverse('sampling:sampling_analysis_spectrophotometry', args=[self.analysis.pk]))
        self.assertContains(response, 'Absorbancia')
        self.assertContains(response, 'Gramos de Muestra')

    def test_vista_registra_procesamiento_espectrofotometrico(self):
        """La vista crea el procesamiento y actualiza el análisis con el resultado."""
        self.client.force_login(self.user)
        url = reverse('sampling:sampling_analysis_spectrophotometry', args=[self.analysis.pk])
        response = self.client.post(url, {
            'action': 'add', 'absorbance': '0.5', 'quantity_sample': '10'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})
        processing = SamplingAnalysisProcessing.objects.get(sample_analysis=self.analysis)
        self.assertAlmostEqual(processing.concentration_sample, 12.5, places=6)
        self.analysis.refresh_from_db()
        self.assertAlmostEqual(self.analysis.average_concentration, 12.5, places=6)


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

    def test_detalle_muestra_ecuacion_gravimetrica_con_terminos(self):
        """El detalle muestra la ecuación gravimétrica combinada con sus términos."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Insolubles con Términos',
            code_analytical_method='GRA-05',
            sample_size=100.0,
            type_method='Gravimetrico',
            laboratory=self.method.laboratory,
            sig_figs_result=4,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', gross_weight='Peso Filtro + Residuo')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', weight_of_filter='Peso Filtro')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Denominador', sample_quantity='Peso de Muestra')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, position='Numerador', factor=100.0)
        GravimetryTerm.objects.create(
            analytical_method=method, term_type='constant', constant_value=100, consecutive=1)
        GravimetryTerm.objects.create(
            analytical_method=method, term_type='basic', operation='subtract', consecutive=2)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[analysis.pk]))

        self.assertEqual(response.status_code, 200)
        equation = response.context['method_equation']
        self.assertIn(r'100 - \left(\frac', equation)
        self.assertIn(r'\text{Residuo}', equation)

    def test_detalle_muestra_ecuacion_espectrofotometrica(self):
        """El detalle muestra la ecuación espectrofotométrica con todos sus campos asociados."""
        method = AnalyticalMethod.objects.create(
            description_analytical_method='Fósforo Espectrofotométrico',
            code_analytical_method='ESP-01',
            sample_size=20.0,
            type_method='Espectrofotometrico',
            laboratory=self.method.laboratory,
        )
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, calculate_description='Concentración',
            unit_measure_calculate='mg/L')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, absorbance='Absorbancia', position='Numerador')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, sample_quantity='Gramos de Muestra', position='Denominador')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, factor=2.5, position='Numerador')
        AnalyticalMethodCalculate.objects.create(
            analytical_method=method, factor=100, term_type='constant',
            operation='multiply', consecutive=2)
        analysis = SamplingAnalysis.objects.create(
            sampling_process=self.analysis.sampling_process, analytical_method=method)

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('sampling:detail_sampling_analysis', args=[analysis.pk]))

        self.assertEqual(response.status_code, 200)
        equation = response.context['method_equation']
        self.assertIn(r'\text{Concentración}', equation)
        self.assertIn(r'\text{Absorbancia}', equation)
        self.assertIn(r'\text{Gramos de Muestra}', equation)
        self.assertIn(r'\frac{\text{Absorbancia}}{\text{Gramos de Muestra}}', equation)
        self.assertIn(r'2.5', equation)
        self.assertIn(r'\times 100', equation)

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
