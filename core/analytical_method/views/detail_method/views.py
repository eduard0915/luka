from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodSolution, AnalyticalMethodSolutionStd, \
    AnalyticalMethodReagent, AnalyticalMethodEquipment, AnalyticalMethodMaterial, AnalyticalMethodProcedure
from core.analytical_method.forms import AnalyticalMethodSolutionForm, AnalyticalMethodSolutionStdForm, \
    AnalyticalMethodReagentForm, AnalyticalMethodEquipmentForm, AnalyticalMethodMaterialForm, AnalyticalMethodProcedureForm


class BaseAnalyticalMethodDetailView(ValidatePermissionRequiredMixin):
    permission_required = 'analytical_method.view_analyticalmethod'
    template_name = 'modal_one.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                analytical_method = AnalyticalMethod.objects.get(pk=self.kwargs.get('pk'))
                form = self.get_form_class()(request.POST, analytical_method=analytical_method)
            elif action == 'edit':
                self.object = self.get_object()
                form = self.get_form()
            else:
                data['error'] = 'No ha ingresado una acción válida'
                return JsonResponse(data)

            if form.is_valid():
                form.save()
                messages.success(request, f'Operación realizada con éxito!')
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


# Soluciones
class AnalyticalMethodSolutionCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodSolution
    form_class = AnalyticalMethodSolutionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Solución'
        context['action'] = 'add'
        return context


class AnalyticalMethodSolutionUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodSolution
    form_class = AnalyticalMethodSolutionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Solución'
        context['action'] = 'edit'
        return context


# Soluciones Estándar
class AnalyticalMethodSolutionStdCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodSolutionStd
    form_class = AnalyticalMethodSolutionStdForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Solución Estándar'
        context['action'] = 'add'
        return context


class AnalyticalMethodSolutionStdUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodSolutionStd
    form_class = AnalyticalMethodSolutionStdForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Solución Estándar'
        context['action'] = 'edit'
        return context


# Reactivos
class AnalyticalMethodReagentCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodReagent
    form_class = AnalyticalMethodReagentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Reactivo'
        context['action'] = 'add'
        return context


class AnalyticalMethodReagentUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodReagent
    form_class = AnalyticalMethodReagentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Reactivo'
        context['action'] = 'edit'
        return context


# Equipos
class AnalyticalMethodEquipmentCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodEquipment
    form_class = AnalyticalMethodEquipmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Equipo'
        context['action'] = 'add'
        return context


class AnalyticalMethodEquipmentUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodEquipment
    form_class = AnalyticalMethodEquipmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Equipo'
        context['action'] = 'edit'
        return context


# Materiales
class AnalyticalMethodMaterialCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodMaterial
    form_class = AnalyticalMethodMaterialForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Material'
        context['action'] = 'add'
        return context


class AnalyticalMethodMaterialUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodMaterial
    form_class = AnalyticalMethodMaterialForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Material'
        context['action'] = 'edit'
        return context


# Procedimientos
class AnalyticalMethodProcedureCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodProcedure
    form_class = AnalyticalMethodProcedureForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Procedimiento'
        context['action'] = 'add'
        return context


class AnalyticalMethodProcedureUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    model = AnalyticalMethodProcedure
    form_class = AnalyticalMethodProcedureForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Procedimiento'
        context['action'] = 'edit'
        return context


# Eliminación genérica para detalles
class AnalyticalMethodDetailDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    permission_required = 'analytical_method.view_analyticalmethod'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
            messages.success(request, 'Eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)
