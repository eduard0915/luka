"""Vistas para la gestión de capacitaciones de usuarios."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import TrainingForm, TrainingUpdateForm, TrainingCreateForm
from core.user.models import Training, User
from core.utils import redirect_to_file


# Registro de capacitación
class TrainingCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar una nueva capacitación asociada a un usuario."""
    model = Training
    form_class = TrainingForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Deshabilita la protección CSRF para esta vista."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario para registrar una nueva capacitación."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Capacitación Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Inyecta el usuario al que se asociará la capacitación en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        user = User.objects.get(slug=self.kwargs.get('pk'))
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de creación de capacitación."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Capacitación'
        return context


# Registro de actualización de capacitación
class TrainingCreateUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar una actualización de una capacitación existente."""
    model = Training
    form_class = TrainingCreateForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Deshabilita la protección CSRF para esta vista."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario para registrar una actualización de capacitación."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Capacitación Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Inyecta la capacitación original en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        training = Training.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'training': training})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de actualización de capacitación."""
        context = super().get_context_data(**kwargs)
        training = Training.objects.get(pk=self.kwargs.get('pk'))
        context['action'] = 'add'
        context['entity'] = 'Registro de Actualización de Capacitación'
        context['info_form'] = str(training)
        return context


# Edición de capacitación
class TrainingUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar una capacitación existente."""
    model = Training
    form_class = TrainingUpdateForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto de capacitación antes de procesar la solicitud."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario para editar una capacitación existente."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Capacitación editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de edición de capacitación."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Capacitación'
        context['action'] = 'edit'
        return context


# Descarga de soporte de capacitación
class TrainingDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para descargar el soporte de una capacitación."""
    permission_required = 'user.view_user'

    @staticmethod
    def get(request):
        """Redirige al soporte de la capacitación alojado en el storage."""
        docid = request.GET.get('id')
        doctype = request.GET.get('type')
        if not docid or not doctype:
            return HttpResponse('La solicitud es incorrecta, faltan parámetros', status=400)
        if doctype != 'support_training':
            return HttpResponse('El documento solicitado no existe para el tipo de archivo', status=404)
        try:
            document = Training.objects.get(id=docid)
        except Training.DoesNotExist:
            return HttpResponse('El documento solicitado no existe', status=404)
        return redirect_to_file(document.support_training)


# Eliminación de capacitación
class TrainingDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar un registro de capacitación."""
    model = Training
    template_name = 'training/delete_training.html'
    permission_required = 'user.view_user'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto de capacitación antes de procesar la solicitud de eliminación."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la eliminación de la capacitación y retorna una respuesta JSON."""
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Registro de Capacitación Eliminado Satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de confirmación de eliminación."""
        context = super().get_context_data(**kwargs)
        t = Training.objects.get(pk=self.kwargs.get('pk'))
        context['entity'] = 'Eliminar de Registro'
        context['delete'] = 'Está seguro de eliminar capacitación?'
        context['info_delete'] = f'{t.description_training}?'
        return context
