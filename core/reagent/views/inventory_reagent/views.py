"""Vistas de la funcionalidad de inventario de reactivos.

Define las vistas para el registro, listado, detalle, edición, eliminación,
transferencia de inventario de reactivos y descarga de certificados de calidad.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import InventoryReagentForm, InventoryReagentTransferForm
from core.reagent.models import InventoryReagent, TransactionReagent, Reagent
from core.solution.models import SolutionStd, code_solution_std_generator, TransactionSolutionStd, SolutionStdBase
from core.solution.services import transfer_inventory_reagent_to_std
from core.utils import redirect_to_file


class InventoryReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar una entrada de reactivo al inventario."""

    model = InventoryReagent
    form_class = InventoryReagentForm
    template_name = 'inventory_reagent/create_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición inicializando el objeto como None."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de registro de inventario de reactivo vía AJAX."""
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
                    data['success'] = True
                    data['redirect_url'] = self.success_url
                else:
                    messages.error(request, form.errors)
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con los datos de la vista."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Entrada de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Registro de Entrada de Reactivos'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


class InventoryReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para listar el inventario de reactivos."""

    model = InventoryReagent
    template_name = 'inventory_reagent/list_inventory_reagent.html'
    permission_required = 'reagent.view_inventoryreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición sin inicializar el objeto."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Retorna los datos del inventario de reactivos en formato JSON para DataTables."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                if request.user.laboratory:
                    inventory_reagents = list(InventoryReagent.objects.values(
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
                    ).filter(reagent__site=request.user.laboratory.site).order_by('-date_creation'))
                else:
                    inventory_reagents = []
                return JsonResponse(inventory_reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla con los datos de la vista."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inventario de Reactivos'
        context['create_url'] = reverse_lazy('reagent:register_inventory_reagent')
        context['entity'] = 'Inventario de Reactivos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vial-virus'
        context['today'] = timezone.now()
        return context


class InventoryReagentDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista para mostrar el detalle de un registro de inventario de reactivo."""

    model = InventoryReagent
    template_name = 'inventory_reagent/detail_inventory_reagent.html'
    permission_required = 'reagent.view_reagent'
    queryset = InventoryReagent.objects.select_related('reagent')

    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Retorna el contexto incluyendo las transacciones asociadas al inventario."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle Movimiento de Reactivo'
        context['entity'] = 'Detalle Movimiento de Reactivo'
        context['label_url'] = reverse_lazy('solution:solution_label_pdf', kwargs={'pk': self.object.pk})
        context['icon'] = 'fa-solid fa-flask-vial'
        context['back'] = reverse_lazy('reagent:list_inventory_reagent')
        context['transactions'] = TransactionReagent.objects.select_related('user_transaction').filter(reagent_inventory_id=self.object.pk)
        return context


class InventoryReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar un registro de entrada de inventario de reactivo."""

    model = InventoryReagent
    form_class = InventoryReagentForm
    template_name = 'inventory_reagent/create_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
    permission_required = 'reagent.change_inventoryreagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición obteniendo el objeto a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de inventario de reactivo."""
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
        """Retorna el contexto de la plantilla con los datos de edición."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Inventario de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Edición Inventario de Reactivo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


class InventoryReagentDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar un registro de inventario de reactivo."""

    model = InventoryReagent
    template_name = 'inventory_reagent/delete_inventory_reagent.html'
    permission_required = 'reagent.delete_inventoryreagent'

    def dispatch(self, request, *args, **kwargs):
        """Despacha la petición obteniendo el objeto a eliminar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Elimina el registro de inventario de reactivo y retorna una respuesta JSON."""
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Entrada de Inventario de reactivo eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla de confirmación de eliminación."""
        context = super().get_context_data(**kwargs)
        ir = InventoryReagent.objects.select_related('reagent').get(pk=self.kwargs.get('pk'))
        context['entity'] = 'Eliminar Inventario de Reactivo'
        context['delete'] = 'Está seguro de eliminar la entrada de inventario de reactivo?'
        context['info_delete'] = f'Lote: {ir.batch_number} - {ir.reagent.code_reagent} {ir.reagent.description_reagent}?'
        return context


class InventoryReagentTransferView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para transferir un reactivo del inventario a una solución estándar."""

    model = InventoryReagent
    form_class = InventoryReagentTransferForm
    template_name = 'inventory_reagent/transfer_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
    permission_required = 'reagent.change_inventoryreagent'

    def dispatch(self, request, *args, **kwargs):
        """Verifica que el reactivo esté marcado como listo para usar antes de continuar."""
        self.object = self.get_object()
        if not self.object.reagent.ready_to_use:
            messages.error(request, 'Este reactivo no está marcado como listo para usar.')
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el traslado a solución estándar buscando la SolutionStdBase correspondiente."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                self.object = self.get_object()
                form = self.get_form()
                if form.is_valid():
                    solution_std_base = SolutionStdBase.objects.filter(
                        solute_std_base=self.object.reagent,
                        enable_solution_std=True
                    ).first()

                    if not solution_std_base:
                        data['error'] = 'No se encontró una Solución Estándar Base habilitada para este reactivo. Por favor, verifique la configuración.'
                        return JsonResponse(data)

                    solution = transfer_inventory_reagent_to_std(self.object.id, solution_std_base, request.user)

                    messages.success(request, f'Traslado a Solución Estándar "{solution.code_solution_std}" realizado con éxito.')
                    data['success'] = True
                    data['redirect_url'] = self.success_url
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Retorna el contexto de la plantilla de traslado."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Traslado a Solución Estándar'
        context['list_url'] = self.success_url
        context['entity'] = 'Traslado a Solución Estándar'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-exchange-alt'
        return context


class CertificateQualityDownloadView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para descargar el certificado de calidad de un reactivo."""

    permission_required = 'reagent.view_reagent'

    @staticmethod
    def get(request):
        """Redirige al certificado de calidad del inventario alojado en el storage."""
        doc_id = request.GET.get('id')
        doc_type = request.GET.get('type')
        if not doc_id or not doc_type:
            return HttpResponse('La solicitud es incorrecta, faltan parámetros', status=400)
        if doc_type != 'certificate_quality':
            return HttpResponse('El documento solicitado no existe para el tipo de archivo', status=404)
        try:
            document = InventoryReagent.objects.get(id=doc_id)
        except InventoryReagent.DoesNotExist:
            return HttpResponse('El documento solicitado no existe', status=404)
        return redirect_to_file(document.certificate_quality)


@require_http_methods(["GET"])
def get_reagent_info(request, reagent_id):
    """Retorna información de un reactivo en formato JSON para consumo AJAX."""
    try:
        reagent = Reagent.objects.get(id=reagent_id)
        return JsonResponse({
            'volumetric': reagent.volumetric,
            'purity_unit': reagent.purity_unit,
            'umb': reagent.umb,
            'description': reagent.description_reagent
        })
    except Reagent.DoesNotExist:
        return JsonResponse({'error': 'Reactivo no encontrado'}, status=404)
