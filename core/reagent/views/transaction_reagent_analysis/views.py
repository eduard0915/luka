"""Vistas CRUD para las transacciones (usos) de reactivos en análisis de muestra.

Registra el consumo de reactivos de inventario durante el análisis de una muestra,
descontando la cantidad usada de `InventoryReagent.quantity_stock` y vinculando
cada transacción a la `SamplingAnalysis` correspondiente.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DeleteView

from core.analytical_method.models import AnalyticalMethodReagent
from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import TransactionReagentAnalysisForm, TransactionReagentAnalysisUpdateForm
from core.reagent.models import TransactionReagent
from core.reagent.services import (
    delete_transaction_reagent_stock,
    register_transaction_reagent,
    update_transaction_reagent_stock,
)
from core.sampling.models import SamplingAnalysis

TRANSACTION_TYPE = 'Uso'


class TransactionReagentAnalysisCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar el uso de un reactivo en un análisis de muestra."""
    model = TransactionReagent
    form_class = TransactionReagentAnalysisForm
    template_name = 'reagent/create_transaction_reagent_analysis.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Carga el análisis y el reactivo del método asociados a la transacción."""
        self.object = None
        self.analysis = get_object_or_404(SamplingAnalysis, pk=self.kwargs.get('analysis_pk'))
        self.analytical_method_reagent = get_object_or_404(
            AnalyticalMethodReagent, pk=self.kwargs.get('amr_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Inyecta el reactivo del método para filtrar el inventario disponible."""
        kwargs = super().get_form_kwargs()
        kwargs['analytical_method_reagent'] = self.analytical_method_reagent
        return kwargs

    def get_initial(self):
        """Precarga la cantidad con la definida en el reactivo del método analítico."""
        initial = super().get_initial()
        initial['quantity'] = self.analytical_method_reagent.amount_reagent
        return initial

    def post(self, request, *args, **kwargs):
        """Procesa el formulario y descuenta la cantidad usada del inventario de reactivo."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    transaction = form.save(commit=False)
                    transaction.sampling_analysis = self.analysis
                    transaction.date_transaction = timezone.now()
                    transaction.type_transaction = TRANSACTION_TYPE
                    transaction.detail_transaction = f'Analisis Muestra {self.analysis}'
                    transaction.user_transaction = request.user
                    transaction.save()
                    register_transaction_reagent(transaction)
                    messages.success(request, 'Uso de reactivo registrado satisfactoriamente!')
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y acción del modal."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registrar Uso de Reactivo'
        return context


class TransactionReagentAnalysisUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar el uso de un reactivo registrado en un análisis."""
    model = TransactionReagent
    form_class = TransactionReagentAnalysisUpdateForm
    template_name = 'reagent/create_transaction_reagent_analysis.html'
    permission_required = 'reagent.change_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene la transacción a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la edición reajustando el stock del inventario de reactivo."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                previous = TransactionReagent.objects.get(pk=self.object.pk)
                previous_quantity = previous.quantity
                previous_inventory_id = previous.reagent_inventory_id
                form = self.get_form()
                if form.is_valid():
                    transaction = form.save()
                    update_transaction_reagent_stock(transaction, previous_quantity, previous_inventory_id)
                    messages.success(request, 'Uso de reactivo actualizado satisfactoriamente!')
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y acción del modal."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'edit'
        context['entity'] = 'Editar Uso de Reactivo'
        return context


class TransactionReagentAnalysisDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar el uso de un reactivo y devolver la cantidad al inventario."""
    model = TransactionReagent
    template_name = 'reagent/delete_transaction_reagent_analysis.html'
    permission_required = 'reagent.delete_reagent'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene la transacción a eliminar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Devuelve la cantidad al inventario y elimina la transacción."""
        data = {}
        try:
            delete_transaction_reagent_stock(self.object)
            self.object.delete()
            messages.success(request, 'Uso de reactivo eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y el mensaje de confirmación del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Uso de Reactivo'
        context['delete'] = '¿Está seguro de eliminar este uso de reactivo?'
        context['info_delete'] = f'{self.object.quantity} {self.object.reagent_inventory.reagent.umb} - {self.object.reagent_inventory}'
        return context
