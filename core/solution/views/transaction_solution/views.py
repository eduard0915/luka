"""Vistas CRUD para las transacciones (usos) de soluciones en análisis de muestra.

Registra el consumo de soluciones preparadas durante el análisis de una muestra,
descontando la cantidad usada de `Solution.quantity_available_sln` y vinculando
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

from core.analytical_method.models import AnalyticalMethodSolution
from core.mixins import ValidatePermissionRequiredMixin
from core.sampling.models import SamplingAnalysis
from core.solution.forms import TransactionSolutionForm, TransactionSolutionUpdateForm
from core.solution.models import TransactionSolution
from core.solution.services import (
    delete_transaction_solution_stock,
    register_transaction_solution,
    update_transaction_solution_stock,
)

TRANSACTION_TYPE = 'Uso'


class TransactionSolutionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para registrar el uso de una solución en un análisis de muestra."""
    model = TransactionSolution
    form_class = TransactionSolutionForm
    template_name = 'solution/create_transaction_solution.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Carga el análisis y la solución del método asociados a la transacción."""
        self.object = None
        self.analysis = get_object_or_404(SamplingAnalysis, pk=self.kwargs.get('analysis_pk'))
        self.analytical_method_solution = get_object_or_404(
            AnalyticalMethodSolution, pk=self.kwargs.get('ams_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Inyecta la solución del método para filtrar el inventario disponible."""
        kwargs = super().get_form_kwargs()
        kwargs['analytical_method_solution'] = self.analytical_method_solution
        return kwargs

    def get_initial(self):
        """Precarga la cantidad con los mililitros definidos en la solución del método."""
        initial = super().get_initial()
        initial['quantity'] = self.analytical_method_solution.milliliter_sln
        return initial

    def post(self, request, *args, **kwargs):
        """Procesa el formulario y descuenta la cantidad usada del inventario de solución."""
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
                    register_transaction_solution(transaction)
                    messages.success(request, 'Uso de solución registrado satisfactoriamente!')
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
        context['entity'] = 'Registrar Uso de Solución'
        return context


class TransactionSolutionUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar el uso de una solución registrado en un análisis."""
    model = TransactionSolution
    form_class = TransactionSolutionUpdateForm
    template_name = 'solution/create_transaction_solution.html'
    permission_required = 'reagent.change_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene la transacción a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la edición reajustando la cantidad disponible de la solución."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                previous = TransactionSolution.objects.get(pk=self.object.pk)
                previous_quantity = previous.quantity
                previous_solution_id = previous.solution_inventory_id
                form = self.get_form()
                if form.is_valid():
                    transaction = form.save()
                    update_transaction_solution_stock(transaction, previous_quantity, previous_solution_id)
                    messages.success(request, 'Uso de solución actualizado satisfactoriamente!')
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
        context['entity'] = 'Editar Uso de Solución'
        return context


class TransactionSolutionDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar el uso de una solución y devolver la cantidad al inventario."""
    model = TransactionSolution
    template_name = 'solution/delete_transaction_solution.html'
    permission_required = 'reagent.change_reagent'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene la transacción a eliminar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Devuelve la cantidad al inventario y elimina la transacción."""
        data = {}
        try:
            delete_transaction_solution_stock(self.object)
            self.object.delete()
            messages.success(request, 'Uso de solución eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y el mensaje de confirmación del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Uso de Solución'
        context['delete'] = '¿Está seguro de eliminar este uso de solución?'
        context['info_delete'] = f'{self.object.quantity} mL - {self.object.solution_inventory}'
        return context
