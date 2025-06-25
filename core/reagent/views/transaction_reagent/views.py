from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import TransactionReagentForm, TransactionReagentUpdateForm
from core.reagent.models import TransactionReagent


# Creación de transacción de reactivo
class TransactionReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = TransactionReagent
    form_class = TransactionReagentForm
    template_name = 'transaction_reagent/create_transaction_reagent.html'
    success_url = reverse_lazy('transaction_reagent:transaction_reagent_list')
    permission_required = 'reagent.add_transactionreagent'
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
                    quantity = form.cleaned_data.get('quantity')
                    messages.success(request, f'Transacción de reactivo por cantidad "{quantity}" creada satisfactoriamente!')
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
        context['title'] = 'Creación de Transacción de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Transacción de Reactivo'
        context['div'] = '10'
        context['icon'] = 'swap_horiz'
        return context


# Listado de transacciones de reactivos
class TransactionReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = TransactionReagent
    template_name = 'transaction_reagent/list_transaction_reagent.html'
    permission_required = 'reagent.view_transactionreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                transaction_reagents = list(TransactionReagent.objects.select_related(
                    'reagent_inventory__reagent'
                ).values(
                    'id',
                    'reagent_inventory__reagent__description_reagent',
                    'reagent_inventory__reagent__code_reagent',
                    'reagent_inventory__batch_number',
                    'date_transaction',
                    'use_register',
                    'quantity',
                    'date_creation',
                    'user_creation__username'
                ).order_by('-date_creation'))
                return JsonResponse(transaction_reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Transacciones de Reactivos'
        context['create_url'] = reverse_lazy('transaction_reagent:transaction_reagent_create')
        context['entity'] = 'Transacciones de Reactivos'
        context['div'] = '11'
        return context


# Edición de transacción de reactivo
class TransactionReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = TransactionReagent
    form_class = TransactionReagentUpdateForm
    template_name = 'transaction_reagent/create_transaction_reagent.html'
    success_url = reverse_lazy('transaction_reagent:transaction_reagent_list')
    permission_required = 'reagent.change_transactionreagent'
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
                    quantity = form.cleaned_data.get('quantity')
                    messages.success(request, f'Transacción de reactivo con cantidad "{quantity}" actualizada satisfactoriamente!')
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
        context['title'] = 'Edición de Transacción de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Edición Transacción de Reactivo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'edit'
        return context


# Eliminación de transacción de reactivo
class TransactionReagentDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = TransactionReagent
    template_name = 'transaction_reagent/delete_transaction_reagent.html'
    success_url = reverse_lazy('transaction_reagent:transaction_reagent_list')
    permission_required = 'reagent.delete_transactionreagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Transacción de reactivo eliminada satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tr = TransactionReagent.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Eliminar Transacción de Reactivo'
        context['entity'] = 'Eliminar Transacción de Reactivo'
        context['delete'] = 'Está seguro de eliminar la transacción de reactivo?'
        context['info_delete'] = f'Cantidad: {tr.quantity} - {tr.reagent_inventory.reagent.description_reagent}?'
        context['list_url'] = self.success_url
        return context
