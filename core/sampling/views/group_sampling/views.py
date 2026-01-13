from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.sampling.forms import SamplingGroupForm
from core.sampling.models import SamplingGroup


# Creación de Grupos de Muestreo
class SamplingGroupCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'sampling.add_samplinggroup'
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
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
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
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Edición de Grupos de Muestreo
class SamplingGroupUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'sampling.change_samplinggroup'
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
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
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


# Listado de Grupos de Muestreo
class SamplingGroupListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SamplingGroup
    template_name = 'group_sampling/list_group.html'
    permission_required = 'sampling.view_samplinggroup'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                groups = SamplingGroup.objects.all()
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
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Detalle de Grupo de Muestreo
class SamplingGroupDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SamplingGroup
    template_name = 'group_sampling/detail_group.html'
    permission_required = 'sampling.view_samplinggroup'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Grupo de Muestreo'
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_group')
        return context
