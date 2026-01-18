from django.db.models.signals import post_save
from django.dispatch import receiver
from core.sampling.models import SamplingProcess, SamplingAnalysis

@receiver(post_save, sender=SamplingProcess)
def create_sampling_analysis(sender, instance, created, **kwargs):
    if not created:
        # Verificar si el estado es 'Confirmada'
        if instance.status_sampling == 'Confirmada':
            # Obtener el punto de muestreo
            sampling_point = None
            if instance.group_sampling:
                sampling_point = instance.group_sampling.sampling_point
            elif instance.point_sampling:
                sampling_point = instance.point_sampling
            
            if sampling_point:
                # Obtener los AnalyticalMethod únicos asociados a través de las especificaciones
                # SamplePoint -> specification (SpecificationProduct) -> method_test (AnalyticalMethodProduct) -> analytical_method
                # Usamos prefetch_related o select_related para eficiencia si fuera necesario, 
                # pero aquí lo hacemos directo para claridad.
                specifications = sampling_point.specification.all()
                analytical_methods = set()
                for spec in specifications:
                    if spec.method_test and spec.method_test.analytical_method:
                        analytical_methods.add(spec.method_test.analytical_method)
                
                # Crear instancias de SamplingAnalysis si no existen para este proceso
                # La descripción dice "el número de instancias a crear debe ser igual a la numero de AnalyticalMethod asociados"
                for method in analytical_methods:
                    SamplingAnalysis.objects.get_or_create(
                        sampling_process=instance,
                        analytical_method=method
                    )
