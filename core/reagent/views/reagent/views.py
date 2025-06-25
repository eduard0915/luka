from urllib.request import urlopen

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from decouple import config
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.models import Reagent
from core.reagent.forms import ReagentForm


# Creación de reactivo
class ReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'
    success_url = reverse_lazy('reagent:list_reagent')
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
                    description_reagent = form.cleaned_data.get('description_reagent')
                    messages.success(request, f'Reactivo "{description_reagent}" creado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Reactivo'
        context['div'] = '8'
        context['icon'] = 'science'
        return context


# Listado de reactivos
class ReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Reagent
    template_name = 'reagent/list_reagent.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                reagents = list(Reagent.objects.values(
                    'id',
                    'description_reagent',
                    'code_reagent',
                    'technical_sheet',
                    'enable_reagent',
                    'manufacturer'
                ).order_by('code_reagent'))
                return JsonResponse(reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reactivos'
        context['create_url'] = reverse_lazy('reagent:create_reagent')
        context['entity'] = 'Reactivos'
        context['div'] = '7'
        context['icon'] = 'science'
        return context


# Edición de reactivo
class ReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'
    success_url = reverse_lazy('reagent:list_reagent')
    permission_required = 'reagent.change_reagent'
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
                    description_reagent = form.cleaned_data.get('description_reagent')
                    messages.success(request, f'Reactivo "{description_reagent}" actualizado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Editar Reactivo'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'edit'
        return context


# Descarga de ficha técnica de reactivo
class ReagentDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'reagent.view_reagent'

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
                document = Reagent.objects.get(id=docid)
            except Reagent.DoesNotExist:
                return HttpResponse('El documento solicitado no existe')
            if document is not None:
                if doctype:
                    if doctype == 'technical_sheet':
                        object_name = 'media/' + str(document.technical_sheet)
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
                        filename = 'ficha_tecnica_' + document.code_reagent + '.' + ext
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
