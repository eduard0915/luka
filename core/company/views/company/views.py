from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from core.company.forms import *
from core.company.models import *
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Empresa
class CompanyCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/create_company.html'
    permission_required = 'company.add_company'

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        try:
            if Company.objects.exists():
                company = Company.objects.first()
                return redirect('company:company_detail', pk=company.id)
        except ObjectDoesNotExist:
            pass
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Empresa configurada satisfactoriamente!')
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
        context['title'] = 'Perfil Empresa'
        context['entity'] = 'Perfil Empresa'
        context['action'] = 'add'
        context['div'] = '10'
        context['list_url'] = reverse_lazy('start:start')
        context['icon'] = 'factory'
        return context


# Edición de Empresa
class CompanyUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/create_company.html'
    permission_required = 'company.change_company'

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
                    messages.success(request, f'La Empresa se ha editado satisfactoriamente!')
                    # Return a direct redirect response instead of relying on client-side redirection
                    return redirect(self.get_context_data()['list_url'])
                else:
                    messages.error(request, form.errors)
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha editado los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Empresa'
        context['entity'] = 'Editar Información Empresa'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': self.kwargs['pk']})
        context['icon'] = 'factory'
        return context


# Detalle de empresa por administrador
class CompanyDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Company
    template_name = 'company/detail_company.html'
    permission_required = 'user.change_user'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super(CompanyDetailView, self).get_queryset()

    def logo(self):
        try:
            return Company.objects.first().get_logo()
        except ObjectDoesNotExist:
            return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Empresa'
        context['entity'] = 'Empresa'
        context['sites'] = Site.objects.filter(company_id=self.object.id)
        context['icon'] = 'bi bi-buildings-fill'
        context['company_logo'] = self.logo()
        return context
