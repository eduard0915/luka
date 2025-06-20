from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.company.forms import StageForm
from core.company.models import Stage
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Etapas
class StageCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Stage
    form_class = StageForm
    template_name = 'stage/create_stage.html'
    permission_required = 'company.add_company'

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
                    messages.success(request, f'Etapa creada satisfactoriamente!')
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
        context['entity'] = 'Creación de Etapa'
        return context


# Edición de Etapa
class StageUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Stage
    form_class = StageForm
    template_name = 'stage/create_stage.html'
    permission_required = 'company.add_company'

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
                    messages.success(request, f'Etapa editada satisfactoriamente!')
                else:
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Etapa'
        context['action'] = 'edit'
        return context
