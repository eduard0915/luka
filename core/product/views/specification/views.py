from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import Product, SpecificationProduct
from core.product.forms import SpecificationProductForm


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


class SpecificationProductCreateView(LoginRequiredMixin, BaseSpecificationProductView, CreateView):
    model = SpecificationProduct
    form_class = SpecificationProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Especificación'
        context['action'] = 'add'
        return context


class SpecificationProductUpdateView(LoginRequiredMixin, BaseSpecificationProductView, UpdateView):
    model = SpecificationProduct
    form_class = SpecificationProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Especificación'
        context['action'] = 'edit'
        return context
