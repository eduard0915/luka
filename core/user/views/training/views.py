from urllib.request import urlopen

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from decouple import config
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import TrainingForm, TrainingUptadeForm
from core.user.models import Training, User


# Registro de capacitación
class TrainingCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

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
                    messages.success(request, f'Capacitación Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = User.objects.get(slug=self.kwargs.get('pk'))
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Capacitación'
        user = User.objects.get(slug=self.kwargs.get('pk'))
        context['user'] = user
        return context


# Edición de capacitación
class TrainingUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingUptadeForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

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
                    messages.success(request, f'Capacitación editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                # return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Capacitación'
        context['action'] = 'edit'
        return context


# Descarga de soporte de capacitacion
class TrainingDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'user.view_user'

    @staticmethod
    def get(request):
        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4', region_name=config('REGION_NAME')))
        docid = request.GET.get('id')
        doctype = request.GET.get('type')
        if docid and doctype:
            try:
                document = Training.objects.get(id=docid)
            except Training.DoesNotExist:
                return HttpResponse('El documento solicitado no existe')
            if document is not None:
                if doctype:
                    if doctype == 'support_training':
                        object_name = 'media/' + str(document.support_training)
                    else:
                        return HttpResponse('El documento solicitado no existe para el tipo de archivo')
                    try:
                        link = s3.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': config('BUCKET'), 'Key': object_name},
                            ExpiresIn=8000
                        )
                        ext = object_name.split(".")[-1]  # Use -1 to get the last element in case of multiple dots
                        url = urlopen(link)
                        doc = url.read()
                        disposition = 'attachment'
                        filename = 'soporte_capacitacion_' + document.description_training + '.' + ext
                        filename = filename.replace(" ", "_")
                        if ext == 'pdf':
                            disposition = 'inline'
                        response = HttpResponse(doc, content_type="application/" + str(ext))
                        response['Content-Disposition'] = str(disposition) + '; filename=' + filename
                        return response
                    except ClientError as e:
                        return HttpResponse(e)
                return None
            else:
                return HttpResponse('El documento solicitado no existe')
        else:
            return HttpResponse('La solicitud es incorrecta, faltan parámetros')


# Eliminación de capacitación
class TrainingDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Training
    template_name = 'training/delete_training.html'
    permission_required = 'user.view_user'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        t = Training.objects.get(pk=self.kwargs.get('pk'))
        context['entity'] = 'Eliminar de Capacitación'
        context['delete'] = 'Está seguro de eliminar capacitación?'
        context['info_delete'] = f'{t.description_training}?'
        return context
