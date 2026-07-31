"""Vistas para el listado de análisis masivos de muestras (Metales Pesados)."""

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView, View

from core.analytical_method.models import AnalyticalMethod
from core.mixins import ValidatePermissionRequiredMixin
from core.sampling.forms import MassiveSampleAnalysisUploadForm
from core.sampling.models import MassiveSampleAnalysis
from core.sampling.services import build_massive_analysis_template, process_massive_analysis_excel
from core.user.models import User
from core.utils import format_form_errors


class MassiveSampleAnalysisListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para el listado de análisis masivos de muestras con filtro avanzado.

    Diseñada para soportar ~250.000 registros anuales mediante paginación
    server-side de DataTables y filtrado en base de datos.
    """
    model = MassiveSampleAnalysis
    template_name = 'massive_analysis_sampling/list_massive_analysis.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Retorna los análisis masivos del sitio del laboratorio del usuario."""
        qs = MassiveSampleAnalysis.objects.select_related(
            'sampling_process',
            'sampling_process__point_sampling__product',
            'sampling_process__group_sampling__sampling_point__product',
            'analytical_method',
            'heavy_metal',
            'analized_by'
        ).prefetch_related('analytical_method__heavymetal_set')
        if self.request.user.laboratory:
            return qs.filter(
                Q(sampling_process__group_sampling__sampling_point__product__site=self.request.user.laboratory.site) |
                Q(sampling_process__point_sampling__product__site=self.request.user.laboratory.site)
            )
        return qs.none()

    def apply_filters(self, qs, request):
        """Aplica los filtros avanzados: fechas, analista, método y muestra."""
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date:
            qs = qs.filter(date_analysis__gte=start_date)
        if end_date:
            qs = qs.filter(date_analysis__lte=end_date + ' 23:59:59')
        if not start_date and not end_date:
            # Por defecto, año actual para limitar el volumen de registros
            qs = qs.filter(date_analysis__year=datetime.now().year)

        analized_by = request.POST.get('analized_by')
        if analized_by:
            qs = qs.filter(analized_by_id=analized_by)

        analytical_method = request.POST.get('analytical_method')
        if analytical_method:
            qs = qs.filter(analytical_method_id=analytical_method)

        sample = request.POST.get('sample', '').strip()
        if sample:
            qs = qs.filter(sampling_process__number_sample__icontains=sample)

        return qs

    def post(self, request, *args, **kwargs):
        """Procesa solicitudes POST de búsqueda (server-side DataTables)."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                draw = int(request.POST.get('draw', 1))
                start = int(request.POST.get('start', 0))
                length = int(request.POST.get('length', 10))

                qs = self.get_queryset()
                records_total = qs.count()

                qs = self.apply_filters(qs, request)
                records_filtered = qs.count()

                order_column = request.POST.get('order[0][column]', '5')
                order_dir = request.POST.get('order[0][dir]', 'desc')
                order_map = {
                    '0': 'sampling_process__number_sample',
                    '2': 'analytical_method__description_analytical_method',
                    '3': 'heavy_metal__metal_description',
                    '4': 'result',
                    '5': 'date_analysis',
                    '6': 'analized_by__first_name',
                }
                order_field = order_map.get(order_column, 'date_analysis')
                if order_dir == 'desc':
                    order_field = '-' + order_field

                qs = qs.order_by(order_field)[start:start + length]

                return JsonResponse({
                    'draw': draw,
                    'recordsTotal': records_total,
                    'recordsFiltered': records_filtered,
                    'data': [i.toJSON() for i in qs]
                })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Agrega el título, entidad y opciones de los filtros al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Metales Pesados'
        context['list_url'] = reverse_lazy('sampling:list_massive_sample_analysis')
        context['entity'] = 'Metales Pesados'
        context['analysts'] = User.objects.filter(
            pk__in=self.get_queryset().exclude(analized_by__isnull=True)
            .values_list('analized_by', flat=True).distinct()
        ).order_by('first_name', 'last_name')
        context['analytical_methods'] = AnalyticalMethod.objects.filter(
            pk__in=self.get_queryset().exclude(analytical_method__isnull=True)
            .values_list('analytical_method', flat=True).distinct()
        ).order_by('description_analytical_method')
        return context


class MassiveSampleAnalysisUploadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    """Vista para el cargue masivo de análisis de metales pesados desde Excel.

    Renderiza el formulario en un modal (GET) y procesa el archivo (POST),
    retornando un resumen JSON con los registros creados y los errores por fila.
    """
    template_name = 'massive_analysis_sampling/upload_massive_analysis.html'
    form_class = MassiveSampleAnalysisUploadForm
    permission_required = 'reagent.add_reagent'
    # permission_required = 'sampling.add_massivesampleanalysis'

    def get_context_data(self, **kwargs):
        """Agrega la entidad y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Cargue Masivo Resultados de Metales Pesados'
        context['action'] = 'upload'
        return context

    def form_valid(self, form):
        """Procesa el archivo Excel y retorna el resumen del cargue."""
        try:
            summary = process_massive_analysis_excel(
                form.cleaned_data['file'], self.request.user
            )
            return JsonResponse(summary)
        except ValueError as e:
            return JsonResponse({'error': str(e)})
        except Exception:
            return JsonResponse({'error': 'No fue posible procesar el archivo. Verifique su contenido.'})

    def form_invalid(self, form):
        """Retorna los errores de validación del formulario."""
        return JsonResponse({'error': format_form_errors(form)})


class MassiveSampleAnalysisTemplateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para descargar la plantilla Excel del cargue masivo de metales pesados.

    Genera un archivo .xlsx con los encabezados fijos y una columna por cada
    metal de los métodos habilitados del laboratorio del usuario, lista para
    pegar o digitar los registros.
    """
    permission_required = 'reagent.add_reagent'

    def get(self, request, *args, **kwargs):
        """Genera y retorna la plantilla Excel como archivo adjunto."""
        buffer = build_massive_analysis_template(request.user)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="Plantilla_Metales_Pesados.xlsx"'
        return response
