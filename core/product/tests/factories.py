"""Factories para los tests de la aplicación product."""

from core.analytical_method.models import (
    AnalyticalMethod, AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation,
    DependentCalculation
)
from core.company.models import Company, Site
from core.laboratory.models import Laboratory
from core.product.models import AnalyticalMethodProduct, Product


def create_company(**kwargs):
    """Crea una compañía de prueba."""
    return Company.objects.create(**kwargs)


def create_site(company=None, **kwargs):
    """Crea una sede de prueba."""
    company = company or create_company()
    defaults = {
        'site_name': 'Sede Prueba',
        'site_address': 'Calle 1 # 2-3',
        'site_city': 'Bogotá',
        'site_country': 'Colombia',
        'company': company,
    }
    defaults.update(kwargs)
    return Site.objects.create(**defaults)


def create_product(site=None, **kwargs):
    """Crea un producto de prueba."""
    site = site or create_site()
    defaults = {
        'code_product': 'PROD-001',
        'description_product': 'Producto de Prueba',
        'site': site,
    }
    defaults.update(kwargs)
    return Product.objects.create(**defaults)


def create_laboratory(site=None, **kwargs):
    """Crea un laboratorio de prueba."""
    site = site or create_site()
    defaults = {'laboratory_name': 'Laboratorio Prueba', 'site': site}
    defaults.update(kwargs)
    return Laboratory.objects.create(**defaults)


def create_analytical_method(laboratory=None, **kwargs):
    """Crea un método analítico de prueba."""
    laboratory = laboratory or create_laboratory()
    defaults = {
        'description_analytical_method': 'Método de Prueba',
        'code_analytical_method': 'MET-001',
        'sample_size': 10,
        'type_method': 'Volumetrico - Mezcla',
        'laboratory': laboratory,
    }
    defaults.update(kwargs)
    return AnalyticalMethod.objects.create(**defaults)


def create_method_calculate(analytical_method=None, product=None, **kwargs):
    """Crea un cálculo base de método analítico de prueba.

    Si se indica product, asocia el método al producto (AnalyticalMethodProduct)
    para que el cálculo aparezca en los querysets filtrados por producto.
    """
    analytical_method = analytical_method or create_analytical_method()
    defaults = {
        'analytical_method': analytical_method,
        'calculate_description': 'Cálculo Base',
    }
    defaults.update(kwargs)
    instance = AnalyticalMethodCalculate.objects.create(**defaults)
    if product is not None:
        AnalyticalMethodProduct.objects.get_or_create(
            product=product, analytical_method=analytical_method)
    return instance


def create_dependent_calculation(product=None, **kwargs):
    """Crea un cálculo dependiente de prueba."""
    product = product or create_product()
    defaults = {
        'calcule_description': 'Cálculo Dependiente',
        'product': product,
        'consecutive': 1,
    }
    defaults.update(kwargs)
    return DependentCalculation.objects.create(**defaults)


def create_calculate_relation(product=None, **kwargs):
    """Crea una relación de cálculo de prueba (sin descripción de cabecera)."""
    product = product or create_product()
    defaults = {'product': product}
    defaults.update(kwargs)
    return AnalyticalMethodCalculateRelation.objects.create(**defaults)
