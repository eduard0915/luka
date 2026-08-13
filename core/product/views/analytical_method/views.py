"""Vistas para la creación y edición de métodos analíticos asignados a productos.

Proporciona la vista base con lógica compartida y las vistas concretas
para crear y editar la relación entre un producto y su método analítico.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import Product, AnalyticalMethodProduct
from core.product.forms import AnalyticalMethodProductForm


class BaseAnalyticalMethodProductView(ValidatePermissionRequiredMixin):
    """Vista base con permisos y lógica compartida para métodos analíticos de producto."""

    permission_required = 'reagent.add_reagent'
    template_name = 'modal_one.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la petición HTTP con protección CSRF desactivada."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la creación o edición de la asignación del método analítico vía AJAX."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                product = Product.objects.get(pk=self.kwargs.get('pk'))
                form = self.get_form_class()(request.POST, product=product)
            elif action == 'edit':
                self.object = self.get_object()
                form = self.get_form()
            elif action == 'delete':
                self.object = self.get_object()
                self.object.delete()
                messages.success(request, 'Método analítico eliminado satisfactoriamente')
                return JsonResponse(data)
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
        """Agrega la clase CSS para el ancho del modal al contexto."""
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


class AnalyticalMethodProductCreateView(LoginRequiredMixin, BaseAnalyticalMethodProductView, CreateView):
    """Vista para agregar un método analítico a un producto."""

    model = AnalyticalMethodProduct
    form_class = AnalyticalMethodProductForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Método Analítico'
        context['action'] = 'add'
        return context


class AnalyticalMethodProductUpdateView(LoginRequiredMixin, BaseAnalyticalMethodProductView, UpdateView):
    """Vista para editar la asignación de un método analítico a un producto."""

    model = AnalyticalMethodProduct
    form_class = AnalyticalMethodProductForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Método Analítico'
        context['action'] = 'edit'
        return context


class AnalyticalMethodProductDeleteView(LoginRequiredMixin, BaseAnalyticalMethodProductView, DeleteView):
    """Vista para eliminar la asignación de un método analítico a un producto."""

    model = AnalyticalMethodProduct
    template_name = 'delete_modal.html'

    def get_context_data(self, **kwargs):
        """Agrega el título, la acción y el mensaje de confirmación al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Método Analítico de Producto'
        context['action'] = 'delete'
        context['delete'] = '¿Está seguro de eliminar este registro?, esta acción es irreversible.'
        context['info_delete'] = f'Se eliminará el método analítico: {self.object.analytical_method}'
        return context
