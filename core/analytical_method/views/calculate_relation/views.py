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
    permission_required = 'analytical_method.view_analyticalmethod'
    template_name = 'modal_one.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.action = request.GET.get('action')
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if isinstance(self, CreateView):
            kwargs['analytical_method'] = AnalyticalMethod.objects.get(pk=self.kwargs.get('pk'))
        else:
            kwargs['analytical_method'] = self.get_object().analytical_method
        return kwargs

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


# Creación de descripción de cálculo relacional
class AnalyticalMethodCalculeRelationDescriptionCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculeRelationDescriptionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción de Cálculo Relacionado a Realizar'
        context['action'] = 'add'
        return context


# Edición de descripción de cálculo relacional
class AnalyticalMethodCalculeRelationDescriptionUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculeRelationDescriptionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción de Cálculo Relacionado a Realizar'
        context['action'] = 'edit'
        return context


# Creación de Cálculo Relacionado
class AnalyticalMethodCalculateRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo Relacionado en la Ecuación'
        context['action'] = 'add'
        return context


# Edición de Cálculo Relacionado
class AnalyticalMethodCalculateRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodCalculateRelationRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo Relacionado en la Ecuación'
        context['action'] = 'edit'
        return context


# Creación Volumen de Estándar Relacional
class AnalyticalMethodVolumenStdRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVolumenStdRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Volumen Estándar Relacional en la Ecuación'
        context['action'] = 'add'
        return context


# Edición Volumen de Estándar Relacional
class AnalyticalMethodVolumenStdRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodVolumenStdRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Volumen Estándar Relacional en la Ecuación'
        context['action'] = 'edit'
        return context


# Creación Factor Relacional
class AnalyticalMethodFactorRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodFactorRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Factor Relacional en la Ecuación'
        context['action'] = 'add'
        return context


# Editar Factor Relacional
class AnalyticalMethodFactorRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodFactorRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Factor Relacional en la Ecuación'
        context['action'] = 'edit'
        return context


# Agregar Cantidad de Muestra Relacional
class AnalyticalMethodSampleGramRelationCreateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, CreateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodSampleGramRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Descripción Cantidad de Muestra Relacional'
        context['action'] = 'add'
        return context


# Editar Cantidad de Muestra Relacional
class AnalyticalMethodSampleGramRelationUpdateView(LoginRequiredMixin, BaseAnalyticalMethodCalculateRelationDetailView, UpdateView):
    model = AnalyticalMethodCalculateRelation
    form_class = AnalyticalMethodSampleGramRelationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción Cantidad de Muestra Relacional'
        context['action'] = 'edit'
        return context


# Eliminación de variable de calculo relacional
class AnalyticalMethodCalculateRelationDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = AnalyticalMethodCalculateRelation
    template_name = 'method/delete_method_calcule.html'
    permission_required = 'analytical_method.view_analyticalmethod'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Variable de Ecuación Relacional eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Variable de Ecuación Relacional'
        context['delete'] = 'Está seguro de eliminar la variable de la ecuación relacional?'
        return context
