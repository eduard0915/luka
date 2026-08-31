"""Tests para la construcción de ecuaciones relacionales con operaciones."""

from django.test import TestCase

from core.product.tests.factories import (
    create_calculate_relation, create_dependent_calculation, create_method_calculate,
    create_product
)
from core.analytical_method.services import _build_relation_equation


class BuildRelationEquationTest(TestCase):
    """Tests de _build_relation_equation: retrocompatibilidad y árbol con operaciones."""

    @classmethod
    def setUpTestData(cls):
        """Crea el producto, el consecutivo y los cálculos base de prueba."""
        cls.product = create_product()
        cls.dep = create_dependent_calculation(product=cls.product)
        cls.calc_g6 = create_method_calculate(calculate_description='G6')
        cls.calc_d9 = create_method_calculate(calculate_description='D9')
        cls.calc_e9 = create_method_calculate(calculate_description='E9')
        cls.calc_f6 = create_method_calculate(calculate_description='F6')
        cls.calc_f9 = create_method_calculate(calculate_description='F9')
        cls.calc_i6 = create_method_calculate(calculate_description='I6')

    def _header(self, **kwargs):
        """Crea la fila cabecera de la ecuación."""
        defaults = {
            'product': self.product,
            'consecutive_calcule': self.dep,
            'calculate_description_relation': 'Mezcla',
            'unit_measure_calculate': '% p/p',
        }
        defaults.update(kwargs)
        return create_calculate_relation(**defaults)

    def test_flat_equation_backward_compatible(self):
        """Una ecuación plana sin operation/parent genera el mismo LaTeX de siempre."""
        header = self._header()
        num_factor = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, factor=2.0, position='Numerador')
        num_calc = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_g6, position='Numerador')
        den_calc = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_d9, position='Denominador')

        equation = _build_relation_equation([header, num_factor, num_calc, den_calc])

        self.assertEqual(
            equation,
            '\\text{Mezcla} \\text{ (% p/p)} = \\frac{2.0 \\times \\text{G6}}{\\text{D9}}'
        )

    def test_equation_without_description_returns_none(self):
        """Sin fila cabecera no se genera ecuación."""
        term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, factor=2.0, position='Numerador')
        self.assertIsNone(_build_relation_equation([term]))

    def test_nested_equation_with_operations(self):
        """Replica 1.774*G6*(((D9-E9)*F6/F9)-(I6/3.722)) con operation y parent."""
        header = self._header()
        factor = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, factor=1.774, position='Numerador')
        g6 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_g6, position='Numerador', operation='multiply')
        group_a = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            position='Numerador', operation='multiply')
        group_b = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, parent=group_a)
        group_c = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            parent=group_a, operation='subtract')
        d9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_d9, parent=group_b, position='Numerador')
        e9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_e9, parent=group_b,
            position='Numerador', operation='subtract')
        f6 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_f6, parent=group_b,
            position='Numerador', operation='multiply')
        f9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_f9, parent=group_b, position='Denominador')
        i6 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_i6, parent=group_c, position='Numerador')
        f3722 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            factor=3.722, parent=group_c, position='Denominador')

        relations = [header, factor, g6, group_a, group_b, group_c, d9, e9, f6, f9, i6, f3722]
        equation = _build_relation_equation(relations)

        self.assertTrue(equation.startswith('\\text{Mezcla} \\text{ (% p/p)} = 1.774 \\times \\text{G6} \\times '))
        self.assertIn('\\left(\\text{D9} - \\text{E9}\\right)', equation)
        self.assertIn('\\frac{\\text{I6}}{3.722}', equation)
        self.assertIn('\\frac{\\left(\\text{D9} - \\text{E9}\\right) \\times \\text{F6}}{\\text{F9}}', equation)

    def test_add_operation_pairs_with_previous_term(self):
        """Un término con operation 'add' se agrupa con el anterior entre paréntesis."""
        header = self._header()
        d9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_d9, position='Numerador')
        e9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_e9, position='Numerador', operation='add')

        equation = _build_relation_equation([header, d9, e9])

        self.assertEqual(
            equation,
            '\\text{Mezcla} \\text{ (% p/p)} = \\left(\\text{D9} + \\text{E9}\\right)'
        )

    def test_divide_operation_sends_term_to_denominator(self):
        """Un término con operation 'divide' pasa al denominador aunque su posición sea Numerador."""
        header = self._header()
        d9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_d9, position='Numerador')
        e9 = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc_e9, position='Numerador', operation='divide')

        equation = _build_relation_equation([header, d9, e9])

        self.assertEqual(
            equation,
            '\\text{Mezcla} \\text{ (% p/p)} = \\frac{\\text{D9}}{\\text{E9}}'
        )
