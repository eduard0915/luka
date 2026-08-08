"""Módulo: Vistas CRUD para la gestión de cálculos relacionados en métodos analíticos."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.analytical_method.forms import *
from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculateRelation
from core.mixins import ValidatePermissionRequiredMixin

class BaseAnalyticalMethodCalculateRelationDetailView(ValidatePermissionRequiredMixin):
    """)Vista base para las operaciones de cálculos relacionados."""
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

# Creación de descripción de cálculo relacional
class AnalyticalMethodCalculeRelationDescriptionCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para crear la descripción de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculeRelationDescriptionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción de Cálculo Relacionado a Realizar'
        context['action'] = 'add'
        return context

# Edición de descripción de cálculo relacional
class AnalyticalMethodCalculeRelationDescriptionUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar la descripción de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculeRelationDescriptionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción de Cálculo Relacionado a Realizar'
        context['action'] = 'edit'
        return context

# Creación de Cálculo Relacionado
class AnalyticalMethodCalculateRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para crear un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo Relacionado en la Ecuación'
        context['action'] = 'add'
        return context

# Edición de Cálculo Relacionado
class AnalyticalMethodCalculateRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo Relacionado en la Ecuación'
        context['action'] = 'edit'
        return context

# Creación de Cálculo Relacionado con Operación
class AnalyticalMethodCalculateRelationOperationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para crear una relación de cálculo del método con operaciones (+, −, ×, ÷) y agrupaciones."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationOperationForm
    template_name = 'modal_four.html'

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo con Operación en la Ecuación'
        context['action'] = 'add'
        return context

# Edición de Cálculo Relacionado con Operación
class AnalyticalMethodCalculateRelationOperationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar una relación de cálculo del método con operaciones."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationOperationForm
    template_name = 'modal_four.html'

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo con Operación en la Ecuación'
        context['action'] = 'edit'
        return context

# Creación Volumen de Estándar Relacional
class AnalyticalMethodVolumenStdRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para agregar volumen estándar a un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVolumenStdRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Volumen Estándar Relacional en la Ecuación'
        context['action'] = 'add'
        return context

# Edición Volumen de Estándar Relacional
class AnalyticalMethodVolumenStdRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar el volumen estándar de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVolumenStdRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Volumen Estándar Relacional en la Ecuación'
        context['action'] = 'edit'
        return context

# Creación Factor Relacional
class AnalyticalMethodFactorRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para agregar un factor constante a un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodFactorRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Factor Relacional en la Ecuación'
        context['action'] = 'add'
        return context

# Editar Factor Relacional
class AnalyticalMethodFactorRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar el factor constante de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodFactorRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Factor Relacional en la Ecuación'
        context['action'] = 'edit'
        return context

# Agregar Cantidad de Muestra Relacional
class AnalyticalMethodSampleGramRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para agregar la variable de muestra a un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodSampleGramRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción Cantidad de Muestra Relacional'
        context['action'] = 'add'
        return context

# Editar Cantidad de Muestra Relacional
class AnalyticalMethodSampleGramRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar la variable de muestra de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodSampleGramRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción Cantidad de Muestra Relacional'
        context['action'] = 'edit'
        return context

# Agregar Variable Relacional
class AnalyticalMethodVariableRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    """)Vista para agregar una variable a un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVariableRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Variable Relacional en la Ecuación'
        context['action'] = 'add'
        return context

# Editar Variable Relacional
class AnalyticalMethodVariableUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    """)Vista para editar la variable de un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVariableRelationForm

    def get_context_data(self, **kwargs):
        """Agrega variables adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Variable Relacional en la Ecuación'
        context['action'] = 'edit'
        return context

# Eliminación de variable de calculo relacional
class AnalyticalMethodCalculateRelationDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """)Vista para eliminar un cálculo relacionado."""
    model = AnalyticalMethodCalculateRelation
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
            messages.success(self.request, 'Variable de Ecuación Relacional eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Variable de Ecuación Relacional'
        context['delete'] = 'Está seguro de eliminar la variable de la ecuación relacional?'
        return context
