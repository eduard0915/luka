import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.laboratory.forms import LaboratoryForm
from core.laboratory.models import Laboratory


# Creación de Laboratorios
class LaboratoryCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'lab/create_laboratory.html'
    permission_required = 'laboratory.add_laboratory'

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
                    self.object = form.save()
                    laboratory_name = form.cleaned_data.get('laboratory_name')
                    messages.success(request, f'Laboratorio "{laboratory_name}" creado satisfactoriamente!')
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
        return reverse('laboratory:list_laboratory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Laboratorio'
        context['action'] = 'add'
        context['entity'] = 'Laboratorios'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('laboratory:list_laboratory')
        return context


# Listado de Laboratorios
class LaboratoryListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Laboratory
    template_name = 'lab/list_laboratory.html'
    permission_required = 'laboratory.view_laboratory'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                laboratories = list(Laboratory.objects.select_related('site').values(
                    'id',
                    'laboratory_name',
                    'site__site_name',
                    'enable_laboratory'
                ).order_by('laboratory_name'))

                # Formatear el estado habilitado
                for lab in laboratories:
                    lab['enable_laboratory_display'] = 'Sí' if lab['enable_laboratory'] else 'No'

                return JsonResponse(laboratories, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Laboratorios'
        context['create_url'] = reverse_lazy('laboratory:create_laboratory')
        context['entity'] = 'Laboratorios'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-flask'
        return context


# Edición de Laboratorios
class LaboratoryUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'lab/update_laboratory.html'
    permission_required = 'laboratory.change_laboratory'

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
                    self.object = form.save()
                    laboratory_name = form.cleaned_data.get('laboratory_name')
                    messages.success(request, f'Laboratorio "{laboratory_name}" editado satisfactoriamente!')
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
        return reverse('laboratory:list_laboratory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Laboratorio'
        context['entity'] = 'Editar Laboratorio'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('laboratory:list_laboratory')
        return context


# Detalle de Laboratorio
class LaboratoryDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Laboratory
    template_name = 'lab/detail_laboratory.html'
    permission_required = 'laboratory.view_laboratory'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Laboratorio'
        context['entity'] = 'Detalle de Laboratorio'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('laboratory:list_laboratory')
        context['update_url'] = reverse_lazy('laboratory:update_laboratory', kwargs={'pk': self.object.pk})
        return context
