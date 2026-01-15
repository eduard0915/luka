from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.sampling.forms import SamplingProcessForm
from core.sampling.models import SamplingProcess
from core.utils import format_form_errors


# Creación de Proceso de Muestreo
class SamplingProcessCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingProcess
    form_class = SamplingProcessForm
    template_name = 'process_sampling/create_process_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_process')
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
                    messages.success(request, f'Proceso de Muestreo creado satisfactoriamente!')
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
        context['entity'] = 'Creación de Muestreo'
        context['title'] = 'Creación de Muestreo'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Edición de Proceso de Muestreo
class SamplingProcessUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplingProcess
    form_class = SamplingProcessForm
    template_name = 'process_sampling/create_process_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_process')
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
                    messages.success(request, f'Proceso de Muestreo editado satisfactoriamente!')
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
        context['title'] = 'Edición de Muestreo'
        context['entity'] = 'Edición de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Listado de Procesos de Muestreo
class SamplingProcessListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SamplingProcess
    template_name = 'process_sampling/list_process_sampling.html'
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
                processes = SamplingProcess.objects.all().order_by('-date_sampling')
                for p in processes:
                    item = {
                        'id': p.id,
                        'group_sampling': str(p.group_sampling),
                        'date_sampling_scheduled': p.date_sampling_scheduled.strftime('%Y-%m-%d %H:%M'),
                        'date_sampling': p.date_sampling.strftime('%Y-%m-%d %H:%M'),
                        'number_sample': p.number_sample,
                        'status_sampling': p.status_sampling,
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
        context['title'] = 'Muestreos'
        context['create_url'] = reverse_lazy('sampling:create_sampling_process')
        context['entity'] = 'Muestreos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vials'
        return context


# Detalle de Proceso de Muestreo
class SamplingProcessDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SamplingProcess
    template_name = 'process_sampling/detail_process_sampling.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Proceso de Muestreo'
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_process')
        return context
