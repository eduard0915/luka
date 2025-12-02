from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.forms import ProductForm
from core.product.models import Product


# Creación de Productos
class ProductCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('product:list_product')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Punto de Muestreo creado satisfactoriamente!')
                else:
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Producto'
        context['title'] = 'Creación de Producto'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


# Edición de Productos
class ProductUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('product:list_product')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Punto de Muestreo editado satisfactoriamente!')
                else:
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Punto de Muestreo'
        context['entity'] = 'Edición de Punto de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


class ProductListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Product
    template_name = 'product/list_product.html'
    permission_required = 'reagent.view_inventoryreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                prod = list(Product.objects.values(
                    'id', 'code_product', 'description_product', 'process__process_name', 'enable_product'
                ).order_by('-date_creation'))
                return JsonResponse(prod, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['create_url'] = reverse_lazy('product:create_product')
        context['entity'] = 'Productos'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context
