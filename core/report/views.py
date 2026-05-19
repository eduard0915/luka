from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import Product, SamplePoint
from core.sampling.models import SamplingAnalysis


class SamplingAnalysisListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SamplingAnalysis
    template_name = 'report/list_sampling_analysis.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                product_id = request.POST.get('product')
                method_id = request.POST.get('analytical_method')

                if not method_id:
                    data = {
                        'columns': [],
                        'data': []
                    }
                else:
                    filters = Q(analytical_method_id=method_id)
                    if product_id:
                        filters &= (
                            Q(sampling_process__point_sampling__product_id=product_id) |
                            Q(sampling_process__group_sampling__sampling_point__product_id=product_id)
                        )

                    analyses = SamplingAnalysis.objects.filter(filters).select_related(
                        'sampling_process__point_sampling',
                        'sampling_process__group_sampling__sampling_point'
                    ).order_by('date_analysis')

                    # Obtener todos los puntos de muestreo asociados al producto
                    sample_points_query = SamplePoint.objects.filter(product_id=product_id).order_by('sequence')
                    sample_points = [p.sample_point_name for p in sample_points_query]

                    # Si no hay puntos de muestreo explícitos para el producto, al menos mostrar los que tienen datos
                    if not sample_points:
                        # Extraer nombres de puntos de muestreo de los análisis
                        # Consideramos tanto point_sampling como group_sampling.sampling_point
                        found_points = set()
                        for a in analyses:
                            if a.sampling_process.point_sampling:
                                found_points.add(a.sampling_process.point_sampling.sample_point_name)
                            elif a.sampling_process.group_sampling and a.sampling_process.group_sampling.sampling_point:
                                found_points.add(a.sampling_process.group_sampling.sampling_point.sample_point_name)
                        sample_points = sorted(list(found_points))

                    # Agrupar datos por fecha y hora
                    rows = {}
                    for a in analyses:
                        dt_str = a.date_analysis.strftime('%Y-%m-%d %H:%M:%S') if a.date_analysis else 'N/A'
                        if dt_str not in rows:
                            rows[dt_str] = {'date_analysis': dt_str}
                            # Inicializar todos los puntos conocidos con vacío o N/A para esta fila
                            for sp in sample_points:
                                rows[dt_str][sp] = '-'
                        
                        # Determinar el nombre del punto de muestreo del análisis actual
                        point_name = None
                        if a.sampling_process.point_sampling:
                            point_name = a.sampling_process.point_sampling.sample_point_name
                        elif a.sampling_process.group_sampling and a.sampling_process.group_sampling.sampling_point:
                            point_name = a.sampling_process.group_sampling.sampling_point.sample_point_name
                        
                        if point_name:
                            # Si el punto no estaba en la lista inicial (ej. producto mal configurado), lo agregamos
                            if point_name not in sample_points:
                                sample_points.append(point_name)
                                # Actualizar filas previas con este nuevo punto
                                for r_key in rows:
                                    if point_name not in rows[r_key]:
                                        rows[r_key][point_name] = '-'
                            
                            rows[dt_str][point_name] = a.average_concentration

                    data = {
                        'columns': sample_points,
                        'data': list(rows.values())
                    }
            elif action == 'search_analytical_method':
                data = []
                product_id = request.POST.get('id')
                if product_id:
                    from core.product.models import AnalyticalMethodProduct
                    methods = AnalyticalMethodProduct.objects.filter(product_id=product_id).select_related('analytical_method')
                    for m in methods:
                        data.append({
                            'id': m.analytical_method.id,
                            'text': f"{m.analytical_method.description_analytical_method}"
                        })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de Análisis de Muestreo'
        context['entity'] = 'Reporte de Análisis de Muestreo'
        context['div'] = '12'
        context['products'] = Product.objects.filter(enable_product=True)
        return context
