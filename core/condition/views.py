from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, View, DetailView

from django.utils import timezone
from core.condition.forms import ConditionForm, ConditionRegisterForm, ConditionRegisterActionsForm
from core.condition.models import Condition, ConditionRegister
from core.mixins import ValidatePermissionRequiredMixin


class ConditionVariableAPI(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'get_variable':
                condition_id = request.POST.get('id')
                if condition_id:
                    condition = Condition.objects.get(pk=condition_id)
                    data['variable'] = condition.variable
                else:
                    data['error'] = 'No se ha proporcionado el ID de la condición'
            else:
                data['error'] = 'No ha ingresado una acción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


class ConditionListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Condition
    template_name = 'condition/list_condition.html'
    permission_required = 'condition.view_condition'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Condition.objects.all():
                    data.append({
                        'id': i.id,
                        'laboratory': i.laboratory.laboratory_name if i.laboratory else 'N/A',
                        'area': i.area,
                        'variable': i.variable,
                        'upper_limit': i.upper_limit,
                        'lower_limit': i.lower_limit,
                        'enabled': 'Sí' if i.enabled else 'No',
                    })
            elif action == 'search_graph':
                data = []
                condition_id = request.POST['id']
                condition = Condition.objects.get(pk=condition_id)
                registers = ConditionRegister.objects.filter(condition_id=condition_id).order_by('-registration_date')[:20]
                for i in reversed(registers):
                    data.append({
                        'date': timezone.localtime(i.registration_date).strftime('%Y-%m-%d %H:%M'),
                        'data': i.registered_data,
                        'upper_limit': condition.upper_limit,
                        'lower_limit': condition.lower_limit,
                    })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Áreas y Condiciones'
        context['create_url'] = reverse_lazy('condition:create_condition')
        context['list_url'] = reverse_lazy('condition:list_condition')
        context['entity'] = 'Áreas y Condiciones'
        context['div'] = '12'
        return context


class ConditionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Condition
    form_class = ConditionForm
    template_name = 'condition/create_condition.html'
    permission_required = 'condition.add_condition'

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
                    messages.success(request, '¡Condición registrada satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('condition:list_condition')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de Área y Condiciones Ambientales'
        context['entity'] = 'Creación de Área y Condiciones Ambientales'
        context['list_url'] = reverse_lazy('condition:list_condition')
        context['action'] = 'add'
        return context


class ConditionUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Condition
    form_class = ConditionForm
    template_name = 'condition/create_condition.html'
    permission_required = 'condition.change_condition'

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
                    messages.success(request, '¡Condición actualizada satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('condition:list_condition')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Área y Condición Ambiental'
        context['entity'] = 'Edición de Área y Condición Ambiental'
        context['list_url'] = reverse_lazy('condition:list_condition')
        context['action'] = 'edit'
        return context


class ConditionRegisterListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = ConditionRegister
    template_name = 'condition/list_condition_register.html'
    permission_required = 'condition.view_conditionregister'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in ConditionRegister.objects.all():
                    data.append({
                        'id': i.id,
                        'registration_date': timezone.localtime(i.registration_date).strftime('%Y-%m-%d %H:%M:%S'),
                        'registered_by': str(i.registered_by),
                        'registered_data': f"{i.registered_data}" '%' if i.condition.variable == 'Humedad Relativa' else f"{i.registered_data}" '°C',
                        'condition__area': f"{i.condition.area}",
                        'condition__variable': f"{i.condition.variable}",
                        'condition__upper_limit': i.condition.upper_limit,
                        'condition__lower_limit': i.condition.lower_limit,
                        'actions_registered_by': i.actions_registered_by.id if i.actions_registered_by else None,
                        'value': i.registered_data,
                    })
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registros de Condiciones Ambientales'
        context['create_url'] = reverse_lazy('condition:create_condition_register')
        context['list_url'] = reverse_lazy('condition:list_condition_register')
        context['entity'] = 'Registros de Condiciones Ambientales'
        context['div'] = '12'
        return context


class ConditionRegisterCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = ConditionRegister
    form_class = ConditionRegisterForm
    template_name = 'condition/create_condition_register.html'
    permission_required = 'condition.add_conditionregister'

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
                    messages.success(request, '¡Registro de condición guardado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('condition:list_condition_register')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Condiciones Ambientales'
        context['entity'] = 'Registro de Condiciones Ambientales'
        context['list_url'] = reverse_lazy('condition:list_condition_register')
        context['action'] = 'add'
        return context


class ConditionRegisterUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = ConditionRegister
    form_class = ConditionRegisterForm
    template_name = 'condition/create_condition_register.html'
    permission_required = 'condition.change_conditionregister'

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
                    messages.success(request, '¡Registro de condición actualizado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('condition:list_condition_register')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Registro de Condiciones Ambientales'
        context['entity'] = 'Edición de Registro de Condiciones Ambientales   '
        context['list_url'] = reverse_lazy('condition:list_condition_register')
        context['action'] = 'edit'
        return context


class ConditionRegisterActionsUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = ConditionRegister
    form_class = ConditionRegisterActionsForm
    template_name = 'modal_two.html'
    permission_required = 'condition.change_conditionregister'

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
                    messages.success(request, '¡Acciones registradas satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Acciones o Correcciones'
        context['entity'] = 'Registro de Acciones o Correcciones'
        context['info_form'] = f"Condición: {self.object.condition} | Dato: {self.object.registered_data}"
        context['action'] = 'edit'
        return context


class ConditionRegisterDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = ConditionRegister
    template_name = 'condition/detail_condition_register.html'
    permission_required = 'condition.view_conditionregister'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Acciones Registradas'
        context['entity'] = 'Detalle de Acciones Registradas'
        return context
