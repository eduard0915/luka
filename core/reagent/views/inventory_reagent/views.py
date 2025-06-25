from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.forms import InventoryReagentForm, InventoryReagentUpdateForm
from core.reagent.models import InventoryReagent


# Creación de inventario de reactivo
class InventoryReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = InventoryReagent
    form_class = InventoryReagentForm
    template_name = 'inventory_reagent/create_inventory_reagent.html'
    success_url = reverse_lazy('reagent:list_inventory_reagent')
    permission_required = 'reagent.add_inventoryreagent'
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
        context['title'] = 'Registro de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Registro de Reactivos'
        context['div'] = '10'
        context['icon'] = 'inventory'
        return context


# Listado de inventario de reactivos
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
                    'batch_number',
                    'date_expire',
                    'quantity_lt',
                    'quantity_ml',
                    'reagent_liquid',
                    'date_creation',
                    'unit_measurement'
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
        context['create_url'] = reverse_lazy('reagent:create_inventory_reagent')
        context['entity'] = 'Inventario de Reactivos'
        context['div'] = '8'
        context['icon'] = 'lab_panel'
        return context


# Edición de inventario de reactivo
class InventoryReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = InventoryReagent
    form_class = InventoryReagentUpdateForm
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
        context['icon'] = 'edit'
        return context


# Eliminación de inventario de reactivo
class InventoryReagentDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = InventoryReagent
    template_name = 'inventory_reagent/delete_inventory_reagent.html'
    success_url = reverse_lazy('inventory_reagent:inventory_reagent_list')
    permission_required = 'reagent.delete_inventoryreagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(self.request, 'Inventario de reactivo eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ir = InventoryReagent.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Eliminar Inventario de Reactivo'
        context['entity'] = 'Eliminar Inventario de Reactivo'
        context['delete'] = 'Está seguro de eliminar el inventario de reactivo?'
        context['info_delete'] = f'Lote: {ir.batch_number} - {ir.reagent.description_reagent}?'
        context['list_url'] = self.success_url
        return context
