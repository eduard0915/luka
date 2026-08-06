from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.mixins import ValidatePermissionRequiredMixin
from core.analytical_method.models import DependentCalculation
from core.analytical_method.forms import DependentCalculationForm
from core.product.models import Product


class BaseDependentCalculationView(ValidatePermissionRequiredMixin):

    permission_required = 'reagent.add_reagent'
    template_name = 'modal_one.html'

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
            elif action == 'delete':
                self.object = self.get_object()
                self.object.delete()
                messages.success(request, 'Operación realizada con éxito!')
                return JsonResponse(data)
            else:
                data['error'] = 'No ha ingresado una acción válida'
                return JsonResponse(data)

            if form.is_valid():
                form.save()
                messages.success(request, 'Operación realizada con éxito!')
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


class DependentCalculationCreateView(LoginRequiredMixin, BaseDependentCalculationView, CreateView):

    model = DependentCalculation
    form_class = DependentCalculationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo Dependiente'
        context['action'] = 'add'
        return context


class DependentCalculationUpdateView(LoginRequiredMixin, BaseDependentCalculationView, UpdateView):

    model = DependentCalculation
    form_class = DependentCalculationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo Dependiente'
        context['action'] = 'edit'
        return context


class DependentCalculationDeleteView(LoginRequiredMixin, BaseDependentCalculationView, DeleteView):

    model = DependentCalculation
    template_name = 'delete_modal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Cálculo Dependiente'
        context['info_delete'] = 'Está seguro de eliminar el Cálculo? esta acción es irreversible'
        context['action'] = 'delete'
        return context
