"""Vistas CRUD para la gestión de especificaciones de productos."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.forms import SpecificationProductForm, SpecificationProductCalculeForm, \
    SpecificationProductCalculeUpdateForm, SpecificationProductUpdateForm
from core.product.models import Product, SpecificationProduct


class BaseSpecificationProductView(ValidatePermissionRequiredMixin):
    """Vista base para las vistas de especificaciones de productos."""
    permission_required = 'reagent.add_reagent'
    template_name = 'modal_three.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición HTTP y aplica decoradores CSRF."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de especificación vía AJAX."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                product = Product.objects.get(pk=self.kwargs.get('pk'))
                form = self.get_form_class()(request.POST, product=product)
            elif action == 'edit':
                self.object = self.get_object()
                form = self.get_form()
            else:
                data['error'] = 'No ha ingresado una acción válida'
                return JsonResponse(data)

            if form.is_valid():
                result = form.save()
                # form.save() atrapa sus propias excepciones y devuelve un dict con 'error'
                if isinstance(result, dict) and result.get('error'):
                    data['error'] = result['error']
                else:
                    messages.success(request, 'Operación realizada con éxito!')
                    product_id = self.kwargs.get('pk') if action == 'add' else self.object.product_id
                    data['success'] = True
                    data['redirect_url'] = reverse('product:detail_product', args=[product_id])
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la clase CSS al contexto del template."""
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


# Asignación de Especificación a Producto
class SpecificationProductCreateView(LoginRequiredMixin, BaseSpecificationProductView, CreateView):
    """Vista para asignar una especificación a un producto."""
    model = SpecificationProduct
    form_class = SpecificationProductForm

    def get_form_kwargs(self):
        """Inyecta el producto como argumento adicional al formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega entidad y acción al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Especificación'
        context['action'] = 'add'
        return context


# Edición de Especificación a Producto
class SpecificationProductUpdateView(LoginRequiredMixin, BaseSpecificationProductView, UpdateView):
    """Vista para editar la especificación de un producto."""
    model = SpecificationProduct
    form_class = SpecificationProductUpdateForm

    def get_form_kwargs(self):
        """Inyecta la especificación actual al formulario."""
        kwargs = super().get_form_kwargs()
        spc = SpecificationProduct.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'spc': spc})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega entidad y acción al contexto de edición."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Especificación'
        context['action'] = 'edit'
        return context


# Asignación de Especificación a Producto desde Calculo
class SpecificationProductCalculeCreateView(LoginRequiredMixin, BaseSpecificationProductView, CreateView):
    """Vista para asignar especificación desde cálculo."""
    model = SpecificationProduct
    form_class = SpecificationProductCalculeForm

    def get_form_kwargs(self):
        """Inyecta el producto al formulario de cálculo."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega entidad y acción al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Especificación'
        context['action'] = 'add'
        return context


# Edición de Asignación Especificación a Producto
class SpecificationProductCalculeUpdateView(LoginRequiredMixin, BaseSpecificationProductView, UpdateView):
    """Vista para editar especificación desde cálculo."""
    model = SpecificationProduct
    form_class = SpecificationProductCalculeUpdateForm

    def get_form_kwargs(self):
        """Inyecta la especificación actual al formulario de cálculo."""
        kwargs = super().get_form_kwargs()
        spc = SpecificationProduct.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'spc': spc})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega entidad y acción al contexto de edición."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Especificación'
        context['action'] = 'edit'
        return context


# Eliminación de Especificación a Producto
class SpecificationProductDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar una especificación de producto."""
    model = SpecificationProduct
    template_name = 'delete_modal.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene la especificación a eliminar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la eliminación de la especificación vía AJAX."""
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Especificación eliminado satisfactoriamente')
            data['success'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega entidad y mensaje de confirmación al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Especificación de Producto'
        context['delete'] = '¿Está seguro de eliminar este registro?, esta acción es irreversible.'
        context['info_delete'] = f'Se eliminará la especificación: {self.object.test_prod}'
        return context
