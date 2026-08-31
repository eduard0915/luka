"""Pruebas unitarias para los formularios de la aplicación sampling."""

from django.test import TestCase

from core.sampling.forms import SamplingGroupForm, SamplingProcessForm
from core.sampling.tests.factories import build_sample_point, build_sampling_group


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
