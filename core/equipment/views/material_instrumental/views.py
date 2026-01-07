from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from core.equipment.forms import MaterialInstrumentalForm
from core.equipment.models import MaterialInstrumental
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Material Instrumental
class MaterialInstrumentalCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = MaterialInstrumental
    form_class = MaterialInstrumentalForm
    template_name = 'material_instrumental/create_material.html'
    permission_required = 'equipment.add_materialinstrumental'

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
                    code_instrumental = form.cleaned_data.get('code_instrumental')
                    messages.success(request, f'Material "{code_instrumental}" creado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            error_messages.extend([str(e) for e in errors])
                        else:
                            field_label = form.fields.get(field, {}).label or field
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
        return reverse('equipment:list_material_instrumental')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Material Instrumental'
        context['action'] = 'add'
        context['entity'] = 'Materiales Instrumentales'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('equipment:list_material_instrumental')
        return context


# Listado de Materiales Instrumentales
class MaterialInstrumentalListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = MaterialInstrumental
    template_name = 'material_instrumental/list_material.html'
    permission_required = 'equipment.view_materialinstrumental'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                materials = list(MaterialInstrumental.objects.select_related(
                    'responsible_user'
                ).values(
                    'id',
                    'code_instrumental',
                    'description_instrumental',
                    'supplier_equipment',
                    'brand_instrumental',
                    'responsible_user__first_name',
                    'responsible_user__last_name',
                    'enable_instrumental'
                ).order_by('-code_instrumental'))

                # Formatear el nombre completo del responsable
                for material in materials:
                    first_name = material.get('responsible_user__first_name', '') or ''
                    last_name = material.get('responsible_user__last_name', '') or ''
                    material['responsible_user__full_name'] = f"{first_name} {last_name}".strip()

                    # Formatear estado
                    material['enable_instrumental_display'] = 'Sí' if material['enable_instrumental'] else 'No'

                return JsonResponse(materials, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Materiales Instrumentales'
        context['create_url'] = reverse_lazy('equipment:create_material_instrumental')
        context['entity'] = 'Materiales Instrumentales'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask'
        return context


# Edición de Materiales Instrumentales
class MaterialInstrumentalUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = MaterialInstrumental
    form_class = MaterialInstrumentalForm
    template_name = 'material_instrumental/update_material.html'
    permission_required = 'equipment.change_materialinstrumental'

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
                    code_instrumental = form.cleaned_data.get('code_instrumental')
                    messages.success(request, f'Material "{code_instrumental}" editado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            error_messages.extend([str(e) for e in errors])
                        else:
                            field_label = form.fields.get(field, {}).label or field
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
        return reverse('equipment:list_material_instrumental')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Material Instrumental'
        context['entity'] = 'Editar Material Instrumental'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('equipment:list_material_instrumental')
        return context


# Detalle de Material Instrumental
class MaterialInstrumentalDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = MaterialInstrumental
    template_name = 'material_instrumental/detail_material.html'
    permission_required = 'equipment.view_materialinstrumental'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Material Instrumental'
        context['entity'] = 'Detalle de Material Instrumental'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('equipment:list_material_instrumental')
        context['update_url'] = reverse_lazy('equipment:update_material_instrumental', kwargs={'pk': self.object.pk})
        return context
