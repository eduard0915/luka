"""Módulo: Vistas CRUD para la gestión de recursos asociados a métodos analíticos (soluciones, reactivos, equipos, materiales, procedimientos)."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.analytical_method.models import *
from core.analytical_method.forms import *

class BaseAnalyticalMethodDetailView(ValidatePermissionRequiredMixin):
    """)Vista base para gestionar los recursos asociados a un método analítico."""
    permission_required = 'analytical_method.view_analyticalmethod'
    template_name = 'modal_one.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición HTTP y aplica decoradores CSRF."""
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Obtiene el parámetro de acción de la petición GET."""
        self.action = request.GET.get('action')
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Inyecta argumentos adicionales al formulario según el contexto."""
        kwargs = super().get_form_kwargs()
        if isinstance(self, CreateView):
            kwargs['analytical_method'] = AnalyticalMethod.objects.get(pk=self.kwargs.get('pk'))
        else:
            kwargs['analytical_method'] = self.get_object().analytical_method
        return kwargs

    def post(self, request, *args, **kwargs):
        """Procesa el formulario enviado vía AJAX y retorna la respuesta JSON."""
        data = {}
        try:
            if isinstance(self, CreateView):
                form = self.get_form()
            elif isinstance(self, UpdateView):
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
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context

# Soluciones
class AnalyticalMethodSolutionCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para asociar una solución a un método analítico."""
    model = AnalyticalMethodSolution
    form_class = AnalyticalMethodSolutionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Solución'
        context['action'] = 'add'
        return context

class AnalyticalMethodSolutionUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar la solución asociada a un método analítico."""
    model = AnalyticalMethodSolution
    form_class = AnalyticalMethodSolutionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Solución'
        context['action'] = 'edit'
        return context

# Soluciones Estándar
class AnalyticalMethodSolutionStdCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para asociar una solución estándar a un método analítico."""
    model = AnalyticalMethodSolutionStd
    form_class = AnalyticalMethodSolutionStdForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Solución Estándar'
        context['action'] = 'add'
        return context

class AnalyticalMethodSolutionStdUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar la solución estándar asociada."""
    model = AnalyticalMethodSolutionStd
    form_class = AnalyticalMethodSolutionStdForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Solución Estándar'
        context['action'] = 'edit'
        return context

# Reactivos
class AnalyticalMethodReagentCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para asociar un reactivo a un método analítico."""
    model = AnalyticalMethodReagent
    form_class = AnalyticalMethodReagentForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Reactivo'
        context['action'] = 'add'
        return context

class AnalyticalMethodReagentUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar el reactivo asociado."""
    model = AnalyticalMethodReagent
    form_class = AnalyticalMethodReagentForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Reactivo'
        context['action'] = 'edit'
        return context

# Equipos
class AnalyticalMethodEquipmentCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para asociar un equipo instrumental a un método analítico."""
    model = AnalyticalMethodEquipment
    form_class = AnalyticalMethodEquipmentForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Equipo'
        context['action'] = 'add'
        return context

class AnalyticalMethodEquipmentUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar el equipo asociado."""
    model = AnalyticalMethodEquipment
    form_class = AnalyticalMethodEquipmentForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Equipo'
        context['action'] = 'edit'
        return context

# Materiales
class AnalyticalMethodMaterialCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para asociar un material instrumental a un método analítico."""
    model = AnalyticalMethodMaterial
    form_class = AnalyticalMethodMaterialForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Material'
        context['action'] = 'add'
        return context

class AnalyticalMethodMaterialUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar el material asociado."""
    model = AnalyticalMethodMaterial
    form_class = AnalyticalMethodMaterialForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Material'
        context['action'] = 'edit'
        return context

# Crear pasos Procedimiento
class AnalyticalMethodProcedureCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar un paso de procedimiento a un método analítico."""
    model = AnalyticalMethodProcedure
    form_class = AnalyticalMethodProcedureForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Procedimiento'
        context['action'] = 'add'
        return context

# Editar pasos Procedimiento
class AnalyticalMethodProcedureUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar un paso de procedimiento."""
    model = AnalyticalMethodProcedure
    form_class = AnalyticalMethodProcedureForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Procedimiento'
        context['action'] = 'edit'
        return context

class AnalyticalMethodProcedureDetailView(LoginRequiredMixin, DetailView):
    """)Vista de detalle de un paso de procedimiento."""
    model = AnalyticalMethod
    template_name = 'method/procedure_detail.html'

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['procedures'] = self.object.analyticalmethodprocedure_set.all().order_by('step_procedure')
        return context

# Eliminación genérica para detalles
class AnalyticalMethodDetailDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """)Vista para eliminar un recurso asociado a un método analítico."""
    permission_required = 'analytical_method.view_analyticalmethod'

    def post(self, request, *args, **kwargs):
        """Procesa la eliminación del registro vía AJAX."""
        data = {}
        try:
            self.get_object().delete()
            messages.success(request, 'Eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

# Solución Estándar Adicionada en valoración por Retroceso
class SolutionStdBackValuationCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar una solución estándar de retrovaloración."""
    model = SolutionStdBackValuation
    form_class = SolutionStdBackValuationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Solución Estándar Adicionada en Valoración por Retroceso'
        context['action'] = 'add'
        return context

# Solución Estándar Gastada en valoración por Retroceso
class SolutionStdBackValuationSpentCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar el gasto de solución estándar de retrovaloración."""
    model = SolutionStdBackValuation
    form_class = SolutionStdBackValuationSpentForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Solución Estándar a Gastar en Valoración por Retroceso'
        context['action'] = 'add'
        return context

class SolutionStdBackValuationDeleteView(AnalyticalMethodDetailDeleteView):
    """)Vista para eliminar una solución estándar de retrovaloración."""
    model = SolutionStdBackValuation
    template_name = 'method/delete_method_calcule.html'
    permission_required = 'analytical_method.view_analyticalmethod'

    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición HTTP y aplica decoradores CSRF."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la eliminación del registro vía AJAX."""
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Variable de Ecuación eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Variable de Ecuación'
        context['delete'] = 'Está seguro de eliminar la variable de la ecuación?'
        return context

# Componentes de Corridas (Metales Pesados)
class HeavyMetalCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar un componente de corrida a un método analítico espectroscópico."""
    model = HeavyMetal
    form_class = HeavyMetalForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Componente de Corrida'
        context['action'] = 'add'
        return context

class HeavyMetalUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar un componente de corrida."""
    model = HeavyMetal
    form_class = HeavyMetalForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Componente de Corrida'
        context['action'] = 'edit'
        return context

class HeavyMetalDeleteView(AnalyticalMethodDetailDeleteView):
    """)Vista para eliminar un componente de corrida."""
    model = HeavyMetal
    template_name = 'method/delete_method_calcule.html'
    permission_required = 'analytical_method.view_analyticalmethod'
