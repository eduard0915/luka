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


# Vista Base para las vistas de especificaciones de productos
class BaseSpecificationProductView(ValidatePermissionRequiredMixin):
    permission_required = 'reagent.add_reagent'
    template_name = 'modal_three.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


# Asignación de Especificación a Producto
class SpecificationProductCreateView(LoginRequiredMixin, BaseSpecificationProductView, CreateView):
    model = SpecificationProduct
    form_class = SpecificationProductForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Especificación'
        context['action'] = 'add'
        return context


# Edición de Especificación a Producto
class SpecificationProductUpdateView(LoginRequiredMixin, BaseSpecificationProductView, UpdateView):
    model = SpecificationProduct
    form_class = SpecificationProductUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        spc = SpecificationProduct.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'spc': spc})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Especificación'
        context['action'] = 'edit'
        return context


# Asignación de Especificación a Producto desde Calculo
class SpecificationProductCalculeCreateView(LoginRequiredMixin, BaseSpecificationProductView, CreateView):
    model = SpecificationProduct
    form_class = SpecificationProductCalculeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Especificación'
        context['action'] = 'add'
        return context


# Edición de Asignación Especificación a Producto
class SpecificationProductCalculeUpdateView(LoginRequiredMixin, BaseSpecificationProductView, UpdateView):
    model = SpecificationProduct
    form_class = SpecificationProductCalculeUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        spc = SpecificationProduct.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'spc': spc})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Especificación'
        context['action'] = 'edit'
        return context


# Eliminación de Especificación a Producto
class SpecificationProductDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = SpecificationProduct
    template_name = 'delete_modal.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Especificación eliminado satisfactoriamente')
            data['success'] = True
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Especificación de Producto'
        context['delete'] = '¿Está seguro de eliminar este registro?, esta acción es irreversible.'
        context['info_delete'] = f'Se eliminará la especificación: {self.object.test_prod}'
        return context
