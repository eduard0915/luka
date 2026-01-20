from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SpecificationProduct
from core.sampling.forms import SamplingProcessForm, SamplingProcessImageForm, SamplingProcessConfirmedForm, \
    SamplingAnalysisProcessingForm
from core.sampling.models import SamplingProcess, SamplingAnalysis, SamplingAnalysisProcessing
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
        context['div'] = '12'
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
                # Obtener el estado del filtro si existe
                status_filter = request.POST.get('status_filter', None)
                
                qs = SamplingProcess.objects.select_related(
                    'group_sampling',
                    'point_sampling',
                    'sampling_created_by'
                )
                
                if status_filter:
                    qs = qs.filter(status_sampling=status_filter)

                data = list(qs.values(
                    'id',
                    'group_sampling',
                    'group_sampling__sampling_point__sample_point_code',
                    'group_sampling__sampling_point__sample_point_name',
                    'group_sampling__sampling_point__product__description_product',
                    'date_sampling_scheduled',
                    'sampling_created_by__first_name',
                    'sampling_created_by__last_name',
                    'sampling_created_by__cargo',
                    'number_sample',
                    'point_sampling',
                    'point_sampling__sample_point_code',
                    'point_sampling__sample_point_name',
                    'point_sampling__product__description_product',
                    'status_sampling'
                ).order_by('-date_sampling'))

                # Formatea de campos
                for item in data:
                    if item['date_sampling_scheduled']:
                        item['date_sampling_scheduled'] = item['date_sampling_scheduled'].strftime('%Y-%m-%d %H:%M')
                    first_name = item.get('sampling_created_by__first_name', '') or ''
                    last_name = item.get('sampling_created_by__last_name', '') or ''
                    cargo = item.get('sampling_created_by__cargo', '') or ''
                    item['sampling_created_by__get_full_name'] = f"{first_name} {last_name}, {cargo}".strip()
                    if item['group_sampling']:
                        code_point = item.get('group_sampling__sampling_point__sample_point_code', '') or ''
                        name_point = item.get('group_sampling__sampling_point__sample_point_name', '') or ''
                        prod = item.get('group_sampling__sampling_point__product__description_product', '') or ''
                        item['group_sampling'] = f'{code_point} {name_point} - {prod}'.strip()
                    else:
                        code_point = item.get('point_sampling__sample_point_code', '') or ''
                        name_point = item.get('point_sampling__sample_point_name', '') or ''
                        prod = item.get('point_sampling__product__description_product', '') or ''
                        item['point_sampling'] = f'{code_point} {name_point} - {prod}'.strip()
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
        context['status_filter'] = ''
        return context


# Listado de Muestreos Programados
class SamplingProcessScheduledListView(SamplingProcessListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestreos Programados'
        context['entity'] = 'Muestreos Programados'
        context['status_filter'] = 'Programada'
        return context


# Listado de Muestreos Confirmados
class SamplingProcessConfirmedListView(SamplingProcessListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestreos Confirmados'
        context['entity'] = 'Muestreos Confirmados'
        context['status_filter'] = 'Confirmada'
        return context


# Listado de Muestreos en Proceso
class SamplingProcessInProcessListView(SamplingProcessListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestras En Proceso'
        context['entity'] = 'Muestras En Proceso'
        context['status_filter'] = 'En Proceso'
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

        # Obtener el punto de muestreo
        sampling_point = (
            self.object.group_sampling.sampling_point if self.object.group_sampling
            else self.object.point_sampling
        )

        # Obtener especificaciones
        context['specifications'] = (
            sampling_point.specification.select_related('product', 'method_test').order_by('type_test', 'test_prod')
            if sampling_point else SpecificationProduct.objects.none()
        )

        context['sampling_analysis'] = SamplingAnalysis.objects.select_related('sampling_process').filter(
            sampling_process_id=self.object.id)

        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_process')
        return context




# Actualización de Foto de la Muestra
class SamplingProcessImageUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplingProcess
    form_class = SamplingProcessImageForm
    template_name = 'process_sampling/update_image_sample.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Foto de la muestra actualizada satisfactoriamente!')
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Actualizar Foto de la Muestra'
        context['action'] = 'edit'
        return context


# Confirmación de la Muestra
class SamplingProcessConfirmedUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplingProcess
    form_class = SamplingProcessConfirmedForm
    template_name = 'process_sampling/update_image_sample.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Toma de Muestra Confirmada satisfactoriamente!')
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Confirmación Toma de Muestra'
        context['info_form'] = mark_safe('<span class="text-danger me-2">¿Está seguro de confirmar la toma de la muestra?</span>')
        context['action'] = 'edit'
        return context
