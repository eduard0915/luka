from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SamplePoint
from core.sampling.forms import SamplingGroupForm
from core.sampling.models import SamplingGroup
from core.utils import format_form_errors


# Creación de Grupos de Muestreo
class SamplingGroupCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Grupo de Muestreo creado satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Grupo de Muestreo'
        context['title'] = 'Creación de Grupo de Muestreo'
        context['div'] = '8'
        context['list_url'] = self.success_url
        return context


# Edición de Grupos de Muestreo
class SamplingGroupUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Grupo de Muestreo editado satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Grupo de Muestreo'
        context['entity'] = 'Edición de Grupo de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Vista para obtener los datos de un punto de muestreo
@require_http_methods(["GET"])
def get_sampling_point(request, pk):
    """
    API endpoint para obtener los datos de un punto de muestreo
    """
    try:
        sampling_point = SamplePoint.objects.get(pk=pk)
        data = {
            'id': str(sampling_point.id),
            'sample_frequency': sampling_point.sample_frequency,
            'sample_point_code': sampling_point.sample_point_code,
            'sample_point_name': sampling_point.sample_point_name,
        }
        return JsonResponse(data)
    except SamplePoint.DoesNotExist:
        return JsonResponse({'error': 'Punto de muestreo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Listado de Grupos de Muestreo
class SamplingGroupListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SamplingGroup
    template_name = 'group_sampling/list_group_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                groups = SamplingGroup.objects.filter(enable_sampling_group=True).order_by('sampling_point__sequence')
                for group in groups:
                    item = {
                        'id': group.id,
                        'sampling_point': str(group.sampling_point),
                        'hour_sampling': group.hour_sampling.strftime('%H:%M'),
                        'number_sampling_day': group.number_sampling_day,
                        'enable_sampling_group': group.enable_sampling_group,
                    }
                    data.append(item)
                return JsonResponse(data, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Grupos de Muestreo'
        context['create_url'] = reverse_lazy('sampling:create_sampling_group')
        context['entity'] = 'Grupos de Muestreo'
        context['div'] = '9'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Detalle de Grupo de Muestreo
class SamplingGroupDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SamplingGroup
    template_name = 'group_sampling/detail_group_sampling.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Grupo de Muestreo'
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_group')
        return context
