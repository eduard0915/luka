"""Módulo: Vistas CRUD para la gestión de cálculos de concentración en métodos analíticos."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.analytical_method.forms import *
from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculate
from core.mixins import ValidatePermissionRequiredMixin

class BaseAnalyticalMethodDetailView(ValidatePermissionRequiredMixin):
    """)Vista base para las operaciones de cálculo en métodos analíticos."""
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

# Creación de descripción de cálculo
class AnalyticalMethodCalculeDescriptionCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para crear la descripción de un cálculo en un método analítico."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodCalculeDescriptionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción de Cálculo a Realizar'
        context['action'] = 'add'
        return context

# Edición de descripción de cálculo
class AnalyticalMethodCalculeDescriptionUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar la descripción de un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodCalculeDescriptionForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción de Cálculo a Realizar'
        context['action'] = 'edit'
        return context

# Creación Volumen de Estándar
class AnalyticalMethodVolumenStdCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar el volumen estándar a un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodVolumenStdForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Volumen Estándar en la Ecuación'
        context['action'] = 'add'
        return context

# Edición Volumen de Estándar
class AnalyticalMethodVolumenStdUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar el volumen estándar de un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodVolumenStdForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Volumen Estándar en la Ecuación'
        context['action'] = 'edit'
        return context

# Creación Factor
class AnalyticalMethodFactorCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar un factor constante a un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodFactorForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Factor en la Ecuación'
        context['action'] = 'add'
        return context

# Editar Factor
class AnalyticalMethodFactorUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar el factor constante de un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodFactorForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Factor en la Ecuación'
        context['action'] = 'edit'
        return context

# Agregar Cantidad de Muestra
class AnalyticalMethodSampleGramCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar la variable de muestra a un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodSampleGramForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción Cantidad de Muestra'
        context['action'] = 'add'
        return context

# Agregar Variable a calculo
class AnalyticalMethodVariableCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    """)Vista para agregar una variable adicional a un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodVariableForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción de Variable'
        context['action'] = 'add'
        return context

# Editar Cantidad de Muestra
class AnalyticalMethodSampleGramUpdateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, UpdateView):
    """)Vista para editar la variable de muestra de un cálculo."""
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodSampleGramForm

    def get_context_data(self, **kwargs):
        """Agrega variables de contexto adicionales al template."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción Cantidad de Muestra'
        context['action'] = 'edit'
        return context

# Eliminación de variable de calculo
class AnalyticalMethodCalculateDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """)Vista para eliminar un cálculo de un método analítico."""
    model = AnalyticalMethodCalculate
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
