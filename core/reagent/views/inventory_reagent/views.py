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
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import InventoryReagentForm
from core.reagent.models import InventoryReagent


# Registro de Entrada Inventario de Reactivo
class InventoryReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = InventoryReagent
    form_class = InventoryReagentForm
    template_name = 'inventory_reagent/create_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
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
                    batch_number = form.cleaned_data.get('batch_number')
                    messages.success(
                        request, f'Reactivo con Lote N° "{batch_number}" registrado satisfactoriamente!')
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
        context['title'] = 'Registro de Entrada de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Registro de Entrada de Reactivos'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Inventario de reactivos
class InventoryReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = InventoryReagent
    template_name = 'inventory_reagent/list_inventory_reagent.html'
    permission_required = 'reagent.view_inventoryreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                inventory_reagents = list(InventoryReagent.objects.select_related('reagent').values(
                    'id',
                    'reagent__description_reagent',
                    'reagent__code_reagent',
                    'reagent__purity_unit',
                    'reagent__density_enable',
                    'reagent__umb',
                    'batch_number',
                    'date_expire',
                    'quantity_stock',
                    'date_creation',
                    'purity',
                    'certificate_quality',
                    'density'
                ).order_by('-date_creation'))
                return JsonResponse(inventory_reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inventario de Reactivos'
        context['create_url'] = reverse_lazy('reagent:register_inventory_reagent')
        context['entity'] = 'Inventario de Reactivos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vial-virus'
        context['today'] = timezone.now()
        return context


# Edición de Registro de Entrada Inventario de Reactivo
class InventoryReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = InventoryReagent
    form_class = InventoryReagentForm
    template_name = 'inventory_reagent/create_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
    permission_required = 'reagent.change_inventoryreagent'
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
                    batch_number = form.cleaned_data.get('batch_number')
                    messages.success(request, f'Inventario de reactivo "{batch_number}" actualizado satisfactoriamente!')
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
        context['title'] = 'Edición de Inventario de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Edición Inventario de Reactivo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Eliminación de inventario de reactivo
class InventoryReagentDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = InventoryReagent
    template_name = 'inventory_reagent/delete_inventory_reagent.html'
    permission_required = 'reagent.delete_inventoryreagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Entrada de Inventario de reactivo eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ir = InventoryReagent.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Eliminar Inventario de Reactivo'
        context['entity'] = 'Eliminar Inventario de Reactivo'
        context['delete'] = 'Está seguro de eliminar la entrada de inventario de reactivo?'
        context['info_delete'] = f'Lote: {ir.batch_number} - {ir.reagent.code_reagent} {ir.reagent.description_reagent}?'
        return context


# Descarga de certificado de calidad de reactivo
class CertificateQualityDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'reagent.view_reagent'

    @staticmethod
    def get(request):
        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4', region_name=config('REGION_NAME')))
        doc_id = request.GET.get('id')
        doc_type = request.GET.get('type')
        if doc_id and doc_type:
            try:
                document = InventoryReagent.objects.get(id=doc_id)
            except InventoryReagent.DoesNotExist:
                return HttpResponse('El documento solicitado no existe')
            if document is not None:
                if doc_type:
                    if doc_type == 'certificate_quality':
                        object_name = 'media/' + str(document.certificate_quality)
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
                        filename = 'coa_' + document.batch_number + '.' + ext
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
