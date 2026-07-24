"""Vistas para la gestión de plantas (Site).

Incluye las vistas de creación, edición y detalle de plantas
asociadas a una empresa dentro del sistema LIMS.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DetailView

from core.company.forms import SiteForm, SiteUpdateForm
from core.company.models import Site, Company, Process
from core.mixins import ValidatePermissionRequiredMixin


class SiteCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de una planta asociada a la empresa.

    Permite registrar una nueva planta con su información de ubicación
    y la asigna automáticamente a la empresa existente.
    """
    model = Site
    form_class = SiteForm
    template_name = 'site/create_site.html'
    permission_required = 'company.add_company'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la solicitud con la protección CSRF desactivada."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de creación de planta."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Planta creada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        """Agrega la empresa principal a los argumentos del formulario."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'company': Company.objects.first()})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de creación de planta."""
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['title'] = 'Creación de Planta'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': company.id})
        context['action'] = 'add'
        context['entity'] = 'Creación de Planta'
        context['div'] = '8'
        context['icon'] = 'bi bi-building-fill-add'
        return context


class SiteUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de una planta existente.

    Permite modificar la información de ubicación de una planta
    previamente registrada.
    """
    model = Site
    form_class = SiteUpdateForm
    template_name = 'site/create_site.html'
    permission_required = 'company.add_company'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Despacha la solicitud con la protección CSRF desactivada y obtiene el objeto."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el envío del formulario de edición de planta."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Planta editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el contexto necesario para la plantilla de edición de planta."""
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['title'] = 'Edición de Planta'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': company.id})
        context['entity'] = 'Edición de Planta'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'bi bi-building-fill'
        return context


class SiteDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista de detalle de una planta.

    Muestra la información completa de la planta incluyendo sus procesos
    asociados habilitados.
    """
    model = Site
    template_name = 'site/detail_site.html'
    permission_required = 'company.add_company'

    def dispatch(self, request, *args, **kwargs):
        """Delega el despacho a la clase padre."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega el contexto con los procesos habilitados asociados a la planta."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Planta'
        context['entity'] = 'Planta: ' + self.object.site_name
        context['subtitle'] = 'Información de la planta'
        context['back'] = reverse_lazy('company:company_detail', kwargs={'pk': self.object.company.id})
        context['div'] = '12'
        context['processes'] = Process.objects.select_related('site').filter(site_id=self.object.id, enable_process=True)
        return context
