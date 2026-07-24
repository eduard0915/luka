"""Vistas de la aplicación de observaciones.

Define las vistas para crear y editar observaciones asociadas
a procesos de muestreo.
"""  # noqa: E501

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.mixins import ValidatePermissionRequiredMixin
from core.observation.forms import ObservationForm
from core.observation.models import Observation
from core.utils import format_form_errors


class ObservationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para crear una nueva observación asociada a un proceso de muestreo."""

    model = Observation
    form_class = ObservationForm
    template_name = 'create_observation.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Exenta de CSRF y despacha la solicitud."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación y asocia la observación al muestreo correspondiente."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.sampling_process_id = self.kwargs['pk']
                    instance.save()
                    messages.success(request, f'Observación registrada satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Observaciones'
        context['action'] = 'add'
        return context


class ObservationUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar una observación existente."""

    model = Observation
    form_class = ObservationForm
    template_name = 'create_observation.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto y despacha la solicitud exenta de CSRF."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición y retorna la respuesta JSON."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Observación editada satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Observaciones'
        context['action'] = 'edit'
        return context
