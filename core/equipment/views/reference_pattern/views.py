"""Vistas de patrones de referencia para la gestión de estándares utilizados en verificaciones diarias."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.equipment.forms import ReferencePatternForm, ReferencePatternUpdateForm
from core.equipment.models import ReferencePattern, EquipmentInstrumental
from core.mixins import ValidatePermissionRequiredMixin


class ReferencePatternCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista de creación de patrones de referencia."""

    model = ReferencePattern
    form_class = ReferencePatternForm
    template_name = 'reference_pattern/create_reference_pattern.html'
    permission_required = 'equipment.add_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP aplicando la exención de CSRF."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud POST para registrar un nuevo patrón de referencia."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Patrón de referencia registrado satisfactoriamente')
                    data['success'] = True
                else:
                    data['error'] = form.errors.as_json()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Agrega el equipo instrumental al contexto del formulario."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'equipment_instrumental': EquipmentInstrumental.objects.get(pk=self.kwargs['pk'])})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de creación."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Registrar Patrón de Referencia'
        context['action'] = 'add'
        return context


class ReferencePatternUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista de edición de patrones de referencia."""

    model = ReferencePattern
    form_class = ReferencePatternUpdateForm
    template_name = 'reference_pattern/create_reference_pattern.html'
    permission_required = 'equipment.change_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP obteniendo el objeto a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud POST para actualizar un patrón de referencia existente."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Patrón de referencia actualizado satisfactoriamente')
                    data['success'] = True
                else:
                    data['error'] = form.errors.as_json()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de edición."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Patrón de Referencia'
        context['action'] = 'edit'
        return context


class ReferencePatternDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista de eliminación de patrones de referencia."""

    model = ReferencePattern
    template_name = 'delete_modal.html'
    permission_required = 'equipment.add_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP obteniendo el objeto a eliminar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud POST para eliminar un patrón de referencia."""
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Patrón de referencia eliminado satisfactoriamente')
            data['success'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de confirmación de eliminación."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Patrón de Referencia'
        context['delete'] = '¿Está seguro de eliminar este registro?'
        context['info_delete'] = f'Se eliminará el patrón de referencia: {self.object.description_pattern}'
        return context
