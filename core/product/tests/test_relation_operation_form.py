"""Tests para el formulario de cálculo relacionado con operaciones."""

from django.test import TestCase

from core.product.forms import ProductCalculateRelationOperationForm
from core.product.tests.factories import (
    create_calculate_relation, create_dependent_calculation, create_method_calculate,
    create_product
)


class ProductCalculateRelationOperationFormTest(TestCase):
    """Tests de ProductCalculateRelationOperationForm."""

    @classmethod
    def setUpTestData(cls):
        """Crea el producto, el consecutivo y un cálculo base de prueba."""
        cls.product = create_product()
        cls.dep = create_dependent_calculation(product=cls.product)
        cls.calc = create_method_calculate(calculate_description='G6', product=cls.product)

    def _form_data(self, **kwargs):
        """Retorna los datos base válidos del formulario."""
        data = {
            'analytical_method_calculate': str(self.calc.pk),
            'operation': 'subtract',
            'position': 'Numerador',
            'parent': '',
        }
        data.update(kwargs)
        return data

    def test_save_assigns_product_consecutive_and_operation(self):
        """El formulario guarda la operación y asigna producto y consecutivo."""
        form = ProductCalculateRelationOperationForm(
            data=self._form_data(), product=self.product, dependent_calculation=self.dep)
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.product, self.product)
        self.assertEqual(instance.consecutive_calcule, self.dep)
        self.assertEqual(instance.operation, 'subtract')

    def test_empty_operation_is_saved_as_none(self):
        """La operación vacía equivale a multiplicar y se guarda como None."""
        form = ProductCalculateRelationOperationForm(
            data=self._form_data(operation=''), product=self.product,
            dependent_calculation=self.dep)
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertIsNone(instance.operation)

    def test_parent_queryset_excludes_header_and_other_products(self):
        """El queryset de padres excluye cabeceras y filas de otros productos."""
        header = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            calculate_description_relation='Mezcla', unit_measure_calculate='% p/p')
        term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc, position='Numerador')
        other_product = create_product(code_product='PROD-002')
        other_dep = create_dependent_calculation(product=other_product)
        other_term = create_calculate_relation(
            product=other_product, consecutive_calcule=other_dep,
            analytical_method_calculate=self.calc, position='Numerador')

        form = ProductCalculateRelationOperationForm(
            product=self.product, dependent_calculation=self.dep)
        queryset = form.fields['parent'].queryset

        self.assertIn(term, queryset)
        self.assertNotIn(header, queryset)
        self.assertNotIn(other_term, queryset)

    def test_parent_queryset_excludes_self_on_edit(self):
        """Al editar, el propio registro no aparece como posible padre."""
        term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc, position='Numerador')

        form = ProductCalculateRelationOperationForm(instance=term)

        self.assertNotIn(term, form.fields['parent'].queryset)

    def test_cycle_with_descendant_is_invalid(self):
        """No se puede agrupar un término dentro de sus propios descendientes."""
        parent_term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, position='Numerador')
        child_term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc, position='Numerador', parent=parent_term)

        form = ProductCalculateRelationOperationForm(
            data=self._form_data(parent=str(child_term.pk)),
            instance=parent_term)

        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)
