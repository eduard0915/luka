

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django import forms

from core.mixins import ValidatePermissionRequiredMixin
from core.analytical_method.models import AnalyticalMethod
from core.analytical_method.forms import AnalyticalMethodForm


# Listado de Métodos Analíticos
class AnalyticalMethodListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = AnalyticalMethod
    template_name = 'method/list_method.html'
    permission_required = 'analytical_method.view_analyticalmethod'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                methods = list(
                    AnalyticalMethod.objects.select_related('laboratory').values(
                        'id',
                        'code_analytical_method',
                        'description_analytical_method',
                        'type_method',
                        'sample_size',
                        'sig_figs_result',
                        'enable_analytical_method',
                        'laboratory__laboratory_name',
                    ).order_by('code_analytical_method')
                )

                for m in methods:
                    m['enable_analytical_method_display'] = 'Sí' if m['enable_analytical_method'] else 'No'

                return JsonResponse(methods, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Métodos Analíticos'
        context['create_url'] = reverse_lazy('analytical_method:create_method')
        context['entity'] = 'Métodos Analíticos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vial'
        return context


# Creación de Métodos Analíticos
class AnalyticalMethodCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = AnalyticalMethod
    form_class = AnalyticalMethodForm
    template_name = 'method/create_method.html'
    permission_required = 'analytical_method.add_analyticalmethod'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code = form.cleaned_data.get('code_analytical_method')
                    messages.success(request, f'Método analítico "{code}" creado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
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

    def get_success_url(self):
        return reverse('analytical_method:list_method')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Método Analítico'
        context['action'] = 'add'
        context['entity'] = 'Métodos Analíticos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vial'
        context['list_url'] = reverse_lazy('analytical_method:list_method')
        return context


# Editar Métodos Analíticos
class AnalyticalMethodUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = AnalyticalMethod
    form_class = AnalyticalMethodForm
    template_name = 'method/update_method.html'
    permission_required = 'analytical_method.change_analyticalmethod'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code = form.cleaned_data.get('code_analytical_method')
                    messages.success(request, f'Método analítico "{code}" editado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
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

    def get_success_url(self):
        return reverse('analytical_method:list_method')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Método Analítico'
        context['entity'] = 'Editar Método Analítico'
        context['action'] = 'edit'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vial'
        context['list_url'] = reverse_lazy('analytical_method:list_method')
        return context


# Detalle de Métodos Analíticos
class AnalyticalMethodDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = AnalyticalMethod
    template_name = 'method/detail_method.html'
    permission_required = 'analytical_method.view_analyticalmethod'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Método Analítico: ' + str(self.object.code_analytical_method)
        context['entity'] = self.object
        context['icon'] = 'fa-solid fa-vial'
        context['list_url'] = reverse_lazy('analytical_method:list_method')
        context['update_url'] = reverse_lazy('analytical_method:update_method', kwargs={'pk': self.object.pk})
        context['solutions'] = self.object.analyticalmethodsolution_set.all()
        context['std_solutions'] = self.object.analyticalmethodsolutionstd_set.all()
        context['reagents'] = self.object.analyticalmethodreagent_set.all()
        context['equipments'] = self.object.analyticalmethodequipment_set.all()
        context['materials'] = self.object.analyticalmethodmaterial_set.all()
        context['procedures'] = self.object.analyticalmethodprocedure_set.all()
        return context
