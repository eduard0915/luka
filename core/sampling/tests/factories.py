import itertools
from datetime import time

from core.company.models import Company, Site
from core.product.models import Product, SamplePoint
from core.sampling.models import SamplingGroup

_sequence = itertools.count(1)


def build_sample_point(code='PM1', enable_point=True, sample_type='En Proceso', sample_frequency=None,
                       periodicity='Diaria'):
    company = Company.objects.create()
    site = Site.objects.create(
        site_name='Planta Test',
        site_address='Calle 1',
        site_city='Bogotá',
        site_country='Colombia',
        company=company,
    )
    product = Product.objects.create(
        code_product='PROD1',
        description_product='Producto Test',
        site=site,
    )
    return SamplePoint.objects.create(
        sample_point_code=code,
        sample_point_name=f'Punto {code}',
        sequence=next(_sequence),
        product=product,
        sample_type=sample_type,
        sample_frequency=sample_frequency,
        periodicity=periodicity,
        enable_point=enable_point,
    )


def build_sampling_group(code='PM1', first_hour='07:00:00', per_day=4, enabled=True, point=None):
    if point is None:
        # Coherente con la UI: N = floor(24 / sample_frequency)
        point = build_sample_point(code=code, sample_frequency=24 // per_day if per_day else None)
    return SamplingGroup.objects.create(
        sampling_point=point,
        # time real, no string: la instancia en memoria se usa directo en
        # datetime.combine() dentro de compute_sampling_times
        first_hour_sampling=time.fromisoformat(first_hour),
        number_sampling_day=per_day,
        enable_sampling_group=enabled,
    )
