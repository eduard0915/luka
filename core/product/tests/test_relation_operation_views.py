"""Tests para las vistas de cálculo relacionado con operaciones."""

from django.test import TestCase
from django.urls import reverse

from core.analytical_method.models import AnalyticalMethodCalculateRelation
from core.product.tests.factories import (
    create_calculate_relation, create_dependent_calculation, create_method_calculate,
    create_product
)
from core.user.models import User


class ProductCalculateRelationOperationViewTest(TestCase):
    """Tests de ProductCalculateRelationOperationCreateView y UpdateView."""

    @classmethod
    def setUpTestData(cls):
        """Crea el usuario, producto, consecutivo y cálculo base de prueba."""
        cls.user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123')
        cls.product = create_product()
        cls.dep = create_dependent_calculation(product=cls.product)
        cls.calc = create_method_calculate(calculate_description='G6', product=cls.product)

    def setUp(self):
        """Autentica al usuario administrador."""
        self.client.force_login(self.user)

    def test_create_view_get_renders_modal(self):
        """La vista de creación responde 200 con el formulario del modal."""
        url = reverse('product:add_calc_relation_operation',
                      kwargs={'pk': self.product.pk, 'dep_pk': self.dep.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agregar Cálculo con Operación')

    def test_create_view_post_add_with_operation_and_parent(self):
        """El POST con action 'add' crea la relación con operación y padre."""
        parent_term = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep, position='Numerador')
        url = reverse('product:add_calc_relation_operation',
                      kwargs={'pk': self.product.pk, 'dep_pk': self.dep.pk})
        data = {
            'action': 'add',
            'analytical_method_calculate': str(self.calc.pk),
            'operation': 'subtract',
            'position': 'Numerador',
            'parent': str(parent_term.pk),
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})
        relation = AnalyticalMethodCalculateRelation.objects.get(parent=parent_term)
        self.assertEqual(relation.operation, 'subtract')
        self.assertEqual(relation.product, self.product)
        self.assertEqual(relation.consecutive_calcule, self.dep)

    def test_update_view_post_edit(self):
        """El POST con action 'edit' actualiza la operación de la relación."""
        relation = create_calculate_relation(
            product=self.product, consecutive_calcule=self.dep,
            analytical_method_calculate=self.calc, position='Numerador')
        url = reverse('product:edit_calc_relation_operation', kwargs={'pk': relation.pk})
        data = {
            'action': 'edit',
            'analytical_method_calculate': str(self.calc.pk),
            'operation': 'add',
            'position': 'Denominador',
            'parent': '',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})
        relation.refresh_from_db()
        self.assertEqual(relation.operation, 'add')
        self.assertEqual(relation.position, 'Denominador')

    def test_create_view_post_invalid_action_returns_error(self):
        """Un POST sin acción válida retorna un error en JSON."""
        url = reverse('product:add_calc_relation_operation',
                      kwargs={'pk': self.product.pk, 'dep_pk': self.dep.pk})
        response = self.client.post(url, {'action': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json())
