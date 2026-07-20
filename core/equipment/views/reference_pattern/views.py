from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.equipment.forms import ReferencePatternForm, ReferencePatternUpdateForm
from core.equipment.models import ReferencePattern, EquipmentInstrumental
from core.mixins import ValidatePermissionRequiredMixin


# Creación de patrón de referencia
class ReferencePatternCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = ReferencePattern
    form_class = ReferencePatternForm
    template_name = 'reference_pattern/create_reference_pattern.html'
    permission_required = 'equipment.add_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        kwargs = super().get_form_kwargs()
        kwargs.update({'equipment_instrumental': EquipmentInstrumental.objects.get(pk=self.kwargs['pk'])})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Registrar Patrón de Referencia'
        context['action'] = 'add'
        return context


# Edición de patrón de referencia
class ReferencePatternUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = ReferencePattern
    form_class = ReferencePatternUpdateForm
    template_name = 'reference_pattern/create_reference_pattern.html'
    permission_required = 'equipment.change_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Patrón de Referencia'
        context['action'] = 'edit'
        return context


# Eliminación de patrón de referencia
class ReferencePatternDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = ReferencePattern
    template_name = 'delete_modal.html'
    permission_required = 'equipment.add_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Patrón de referencia eliminado satisfactoriamente')
            data['success'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Patrón de Referencia'
        context['delete'] = '¿Está seguro de eliminar este registro?'
        context['info_delete'] = f'Se eliminará el patrón de referencia: {self.object.description_pattern}'
        return context
