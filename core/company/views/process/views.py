"""Vistas para la gestión de procesos (Process).

Incluye las vistas de creación y edición de procesos asociados
a una planta dentro del sistema LIMS.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.company.forms import ProcessForm, ProcessUpdateForm
from core.company.models import Process, Site
from core.mixins import ValidatePermissionRequiredMixin


class ProcessCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de un proceso asociado a una planta.

    Permite registrar un nuevo proceso indicando la planta a la que
    pertenece mediante el parámetro pk de la URL.
    """
    model = Process
    form_class = ProcessForm
    template_name = 'process/create_process.html'
    permission_required = 'company.add_company'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la solicitud con la protección CSRF desactivada."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de creación de proceso."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Proceso creado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Agrega la planta obtenida de la URL a los argumentos del formulario."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'site': Site.objects.get(pk=self.kwargs.get('pk'))})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de creación de proceso."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Proceso'
        context['class'] = 'col-md-8'
        return context


class ProcessUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de un proceso existente.

    Permite modificar el nombre de un proceso previamente registrado.
    """
    model = Process
    form_class = ProcessUpdateForm
    template_name = 'process/create_process.html'
    permission_required = 'company.add_company'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la solicitud con la protección CSRF desactivada y obtiene el objeto."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de edición de proceso."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Proceso editado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de edición de proceso."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Proceso'
        context['action'] = 'edit'
        return context
