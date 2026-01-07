from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, View, ListView

from core.mixins import ValidatePermissionRequiredMixin
from core.solution.forms import SolutionBaseForm
from core.solution.models import SolutionBase


# Creación de solución base
class SolutionBaseCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SolutionBase
    form_class = SolutionBaseForm
    template_name = 'solution/create_solution_base.html'
    permission_required = 'reagent.add_reagent'

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
                    messages.success(request, f'Solución Base creada satisfactoriamente!')
                    data['success'] = True
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            error_messages.extend([str(e) for e in errors])
                        else:
                            field_label = form.fields[field].label or field
                            for error in errors:
                                error_messages.append(f"{field_label}: {error}")
                    error_text = '<br>'.join(error_messages)
                    messages.error(request, error_text)
                    data['error'] = error_text
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Solución Base'
        context['action'] = 'add'
        context['entity'] = 'Soluciones Base'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution_base')
        return context


# Editar soluciones base
class SolutionBaseUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SolutionBase
    form_class = SolutionBaseForm
    template_name = 'solution/create_solution_base.html'
    permission_required = 'reagent.change_reagent'

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
                    messages.success(request, f'Solución Base actualizada satisfactoriamente!')
                    data['success'] = True
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            error_messages.extend([str(e) for e in errors])
                        else:
                            field_label = form.fields[field].label or field
                            for error in errors:
                                error_messages.append(f"{field_label}: {error}")
                    error_text = '<br>'.join(error_messages)
                    messages.error(request, error_text)
                    data['error'] = error_text
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Solución Base'
        context['action'] = 'edit'
        context['entity'] = 'Soluciones Base'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution_base')
        return context


# Habilitar soluciones base
class SolutionBaseEnableView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'reagent.change_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            instance = SolutionBase.objects.get(pk=kwargs['pk'])
            instance.enable_solution = True
            instance.save()
            data['success'] = True
            messages.success(request, f'Solución Base habilitada correctamente')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


# Deshabilitar soluciones base
class SolutionBaseDisableView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'reagent.change_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            instance = SolutionBase.objects.get(pk=kwargs['pk'])
            instance.enable_solution = False
            instance.save()
            data['success'] = True
            messages.success(request, f'Solución Base deshabilitada correctamente')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)


# Listado de Soluciones Base
class SolutionBaseListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SolutionBase
    template_name = 'solution/list_solution_base.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                reagents = list(SolutionBase.objects.values(
                    'id',
                    'solute_reagent_base__description_reagent',
                    'concentration_base',
                    'concentration_unit_base',
                    'enable_solution'
                ).order_by('-solute_reagent_base__description_reagent'))
                return JsonResponse(reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Maestro de Soluciones'
        context['create_url'] = reverse_lazy('solution:create_solution_base')
        context['entity'] = 'Maestro de Soluciones'
        context['div'] = '7'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context
