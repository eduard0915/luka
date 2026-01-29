from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from core.analytical_method.forms import *
from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculate
from core.mixins import ValidatePermissionRequiredMixin


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


# Creación de descripción de cálculo
class AnalyticalMethodCalculeDescriptionCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodCalculeDescriptionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción de Cálculo a Realizar'
        context['action'] = 'add'
        return context


# Creación Volumen de Estándar
class AnalyticalMethodVolumenStdCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodVolumenStdForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Volumen Estándar en la Ecuación'
        context['action'] = 'add'
        return context


# Creación Factor
class AnalyticalMethodFactorCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodFactorForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Factor en la Ecuación'
        context['action'] = 'add'
        return context


# Agregar Cantidad de Muestra
class AnalyticalMethodSampleGramCreateView(LoginRequiredMixin, BaseAnalyticalMethodDetailView, CreateView):
    model = AnalyticalMethodCalculate
    form_class = AnalyticalMethodSampleGramForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción Cantidad de Muestra'
        context['action'] = 'add'
        return context
