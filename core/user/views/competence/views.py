"""Vistas para la gestión de competencias (certificaciones) de usuarios."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import CompetenceForm, CompetenceUpdateForm
from core.user.models import Competence, User
from core.utils import redirect_to_file


# Registro de competencia
class CompetenceCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar una nueva competencia o certificación de un usuario."""
    model = Competence
    form_class = CompetenceForm
    template_name = 'competence/create_competence.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Deshabilita la protección CSRF para esta vista."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario para registrar una nueva competencia."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Competencia Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Inyecta el usuario al que se asociará la competencia en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        user = User.objects.get(slug=self.kwargs.get('pk'))
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de creación de competencia."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Competencia'
        return context


# Edición de competencia
class CompetenceUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar una competencia existente."""
    model = Competence
    form_class = CompetenceUpdateForm
    template_name = 'competence/create_competence.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Deshabilita la protección CSRF y obtiene el objeto de competencia a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario para editar una competencia."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Competencia editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de edición de competencia."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Competencia'
        context['action'] = 'edit'
        return context


# Descarga de soporte de competencia
class CompetenceDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para descargar el soporte de una competencia."""

    permission_required = 'user.view_user'

    @staticmethod
    def get(request):
        """Redirige al soporte de la competencia alojado en el storage."""
        docid = request.GET.get('id')
        doctype = request.GET.get('type')
        if not docid or not doctype:
            return HttpResponse('La solicitud es incorrecta, faltan parámetros', status=400)
        if doctype != 'support_competence':
            return HttpResponse('El documento solicitado no existe para el tipo de archivo', status=404)
        try:
            document = Competence.objects.get(id=docid)
        except Competence.DoesNotExist:
            return HttpResponse('El documento solicitado no existe', status=404)
        return redirect_to_file(document.support_competence)


# Eliminación de competencia
class CompetenceDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar una competencia."""

    model = Competence
    template_name = 'competence/delete_competence.html'
    permission_required = 'user.view_user'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto de competencia antes de procesar la solicitud."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Elimina la competencia y retorna una respuesta JSON."""
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de confirmación de eliminación."""
        context = super().get_context_data(**kwargs)
        c = Competence.objects.get(pk=self.kwargs.get('pk'))
        context['entity'] = 'Eliminar Competencia'
        context['delete'] = 'Está seguro de eliminar la competencia?'
        context['info_delete'] = f'{c.description_competence}?'
        return context
