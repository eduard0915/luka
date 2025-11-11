from core.mixins import ValidatePermissionRequiredMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.reagent.models import Reagent
from core.solution.forms import StandardizationForm, StandardizationUpdateForm
from core.solution.models import Standardization


# Creación de Configuración de Estandarización
class StandardizationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Standardization
    form_class = StandardizationForm
    template_name = 'standarization/create_std_sln.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, '¡Estandarización Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        reagent = Reagent.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'reagent': reagent})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Configuración de Estandarización'
        return context


# Edición de configuración de estandarización
class StandardizationUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Standardization
    form_class = StandardizationUpdateForm
    template_name = 'standarization/create_std_sln.html'
    permission_required = 'reagent.add_reagent'

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
                    messages.success(request, '¡Estandarización editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Configuración de Estandarización'
        context['action'] = 'edit'
        return context
