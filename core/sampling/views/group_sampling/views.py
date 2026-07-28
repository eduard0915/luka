"""Vistas para la gestión de grupos de muestreo."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import Product, SamplePoint
from core.sampling.forms import SamplingGroupForm, SamplingGroupFullForm
from core.sampling.models import SamplingGroup
from core.utils import format_form_errors


class SamplingGroupListCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de grupos de muestreo."""
    model = SamplingGroup
    form_class = SamplingGroupFullForm
    template_name = 'create_two.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = None
        self.product = None
        if 'pk' in kwargs:
            try:
                self.product = Product.objects.get(pk=kwargs['pk'])
            except Product.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario si existe."""
        kwargs = super().get_form_kwargs()
        if self.product:
            kwargs.update({'product': self.product})
        return kwargs

    def get_success_url(self):
        """Redirige al detalle del producto si se creó desde allí."""
        if self.product:
            return reverse_lazy('product:detail_product', kwargs={'pk': self.product.pk})
        return self.success_url

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación de grupo de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.get_success_url())
                    messages.success(request, f'Grupo de Muestreo creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y configuración de la vista al contexto."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Grupo de Muestreo'
        context['title'] = 'Creación de Grupo de Muestreo'
        context['div'] = '8'
        context['list_url'] = self.get_success_url()
        return context


class SamplingGroupCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de grupos de muestreo."""
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = None
        self.product = None
        if 'pk' in kwargs:
            try:
                self.product = Product.objects.get(pk=kwargs['pk'])
            except Product.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario si existe."""
        kwargs = super().get_form_kwargs()
        if self.product:
            kwargs.update({'product': self.product})
        return kwargs

    def get_success_url(self):
        """Redirige al detalle del producto si se creó desde allí."""
        if self.product:
            return reverse_lazy('product:detail_product', kwargs={'pk': self.product.pk})
        return self.success_url

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación de grupo de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.get_success_url())
                    messages.success(request, f'Grupo de Muestreo creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y configuración de la vista al contexto."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Grupo de Muestreo'
        context['title'] = 'Creación de Grupo de Muestreo'
        context['div'] = '8'
        context['list_url'] = self.get_success_url()
        return context


class SamplingGroupUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de grupos de muestreo."""
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'group_sampling/create_group_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de grupo de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
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
        """Agrega el título y configuración de edición al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Grupo de Muestreo'
        context['entity'] = 'Edición de Grupo de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


class SamplingGroupListUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de grupos de muestreo."""
    model = SamplingGroup
    form_class = SamplingGroupForm
    template_name = 'create_two.html'
    success_url = reverse_lazy('sampling:list_sampling_group')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de grupo de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
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
        """Agrega el título y configuración de edición al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Grupo de Muestreo'
        context['entity'] = 'Edición de Grupo de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Eliminar Grupo de muestreo
class SamplingGroupDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = SamplingGroup
    template_name = 'delete_modal.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Grupo de Muestreo eliminado satisfactoriamente')
            data['success'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Grupo de Muestreo'
        context['delete'] = '¿Está seguro de eliminar este registro?, esta acción es irreversible.'
        context['info_delete'] = f'Se eliminará el grupo de muestreo: {self.object.sampling_point.sample_point_name}'
        return context


@require_http_methods(["GET"])
def get_sampling_point(request, pk):
    """API endpoint para obtener los datos de un punto de muestreo."""
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


class SamplingGroupListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para el listado de grupos de muestreo."""
    model = SamplingGroup
    template_name = 'group_sampling/list_group_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa solicitudes POST para la búsqueda de grupos de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                groups = SamplingGroup.objects.select_related('sampling_point').filter(enable_sampling_group=True).order_by('sampling_point__sequence')
                for group in groups:
                    item = {
                        'id': group.id,
                        'sampling_point': str(group.sampling_point),
                        'first_hour_sampling': group.first_hour_sampling.strftime('%H:%M'),
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
        """Agrega el título y configuración del listado al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Grupos de Muestreo'
        context['create_url'] = reverse_lazy('sampling:create_sampling_group_list')
        context['entity'] = 'Grupos de Muestreo'
        context['div'] = '9'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


class SamplingGroupDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista para el detalle de un grupo de muestreo."""
    model = SamplingGroup
    template_name = 'group_sampling/detail_group_sampling.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud de detalle del grupo."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega el título, entidad e icono al contexto del detalle."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Grupo de Muestreo'
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_group')
        return context
