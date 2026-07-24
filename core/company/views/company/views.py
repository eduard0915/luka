"""Vistas para la gestión de empresas (Company).

Incluye las vistas de creación, edición y detalle de la información
general de la empresa en el sistema LIMS.
"""

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


class CompanyCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de una empresa.

    Si ya existe una empresa registrada, redirige automáticamente al detalle
    de la empresa existente. Maneja el formulario de configuración inicial.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'company/create_company.html'
    permission_required = 'company.add_company'

    def dispatch(self, request, *args, **kwargs):
        """Redirige al detalle de la empresa si ya existe un registro."""
        self.object = None
        try:
            if Company.objects.exists():
                company = Company.objects.first()
                return redirect('company:company_detail', pk=company.id)
        except ObjectDoesNotExist:
            pass
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de creación de empresa."""
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
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de creación de empresa."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Perfil Empresa'
        context['entity'] = 'Perfil Empresa'
        context['action'] = 'add'
        context['div'] = '10'
        context['list_url'] = reverse_lazy('start:start')
        context['icon'] = 'bi bi-building-fill-add'
        return context


class CompanyUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de los datos de la empresa.

    Permite modificar la información general de la empresa configurada
    en el sistema.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'company/create_company.html'
    permission_required = 'company.change_company'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto empresa y delega el despacho a la clase padre."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de edición de empresa."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'La Empresa se ha editado satisfactoriamente!')
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
        """Agrega el contexto necesario para la plantilla de edición de empresa."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Empresa'
        context['entity'] = 'Editar Información Empresa'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': self.kwargs['pk']})
        context['icon'] = 'bi bi-buildings-fill'
        return context


class CompanyDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista de detalle de la empresa.

    Muestra la información completa de la empresa incluyendo sus plantas
    asociadas y el logotipo.
    """
    model = Company
    template_name = 'company/detail_company.html'
    permission_required = 'user.change_user'

    def dispatch(self, request, *args, **kwargs):
        """Delega el despacho a la clase padre."""
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Retorna el conjunto de consultas base para obtener la empresa."""
        return super(CompanyDetailView, self).get_queryset()

    def logo(self):
        """Retorna la URL del logotipo de la empresa o una imagen por defecto."""
        try:
            return Company.objects.first().get_logo()
        except ObjectDoesNotExist:
            return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def get_context_data(self, **kwargs):
        """Agrega el contexto con las plantas asociadas y el logotipo de la empresa."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Empresa'
        context['entity'] = 'Empresa'
        context['sites'] = Site.objects.filter(company_id=self.object.id)
        context['icon'] = 'bi bi-buildings-fill'
        context['company_logo'] = self.logo()
        return context
