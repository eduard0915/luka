"""Vistas de la funcionalidad de reactivos.

Define las vistas para la creación, listado, edición, detalle y descarga
de fichas técnicas de reactivos.
"""

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
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import ReagentForm
from core.reagent.models import Reagent
from core.utils import format_form_errors


class ReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de un nuevo reactivo."""

    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'
    success_url = reverse_lazy('reagent:list_reagent')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición inicializando el objeto como None."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación de reactivo vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    description_reagent = form.cleaned_data.get('description_reagent')
                    messages.success(request, f'Reactivo "{description_reagent}" creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con los datos de creación."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Reactivo'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context


class ReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para listar los reactivos registrados en el sistema."""

    model = Reagent
    template_name = 'reagent/list_reagent.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Retorna los datos de los reactivos en formato JSON para DataTables."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                if request.user.laboratory:
                    reagents = list(Reagent.objects.values(
                        'id',
                        'code_reagent',
                        'description_reagent',
                        'umb',
                        'purity_unit',
                        'manufacturer',
                        'enable_reagent',
                        'technical_sheet',
                        'volumetric',
                        'solvent',
                        'density_enable',
                        'standard'
                    ).filter(site=request.user.laboratory.site).order_by('code_reagent'))
                else:
                    reagents = []
                return JsonResponse(reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con los datos de la vista."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reactivos'
        context['create_url'] = reverse_lazy('reagent:create_reagent')
        context['entity'] = 'Reactivos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context


class ReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de un reactivo existente."""

    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'
    success_url = reverse_lazy('reagent:list_reagent')
    permission_required = 'reagent.change_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición obteniendo el objeto a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de reactivo vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    description_reagent = form.cleaned_data.get('description_reagent')
                    messages.success(request, f'Reactivo "{description_reagent}" actualizado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con los datos de edición."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Editar Reactivo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context


class ReagentDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista para mostrar el detalle de un reactivo."""

    model = Reagent
    template_name = 'reagent/detail_reagent.html'
    permission_required = 'reagent.view_reagent'

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con el objeto reactivo."""
        context = super().get_context_data(**kwargs)
        context['entity'] = self.object
        context['icon'] = 'fa-solid fa-flask-vial'
        return context


class ReagentDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para descargar la ficha técnica de un reactivo desde S3."""

    permission_required = 'reagent.view_reagent'

    @staticmethod
    def get(request):
        """Descarga la ficha técnica desde Amazon S3 usando una URL prefirmada."""
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
                        ext = object_name.split(".")[-1]
                        url = urlopen(link)
                        doc = url.read()
                        disposition = 'attachment'
                        filename = 'sheet_' + document.description_reagent + '.' + ext
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
