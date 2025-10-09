from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from core.company.forms import SiteForm, SiteUpdateForm
from core.company.models import Site, Company, Process, Stage, SamplePoint
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Planta
class SiteCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Site
    form_class = SiteForm
    template_name = 'site/create_site.html'
    permission_required = 'company.add_company'

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
                    messages.success(request, f'Planta creada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'company': Company.objects.first()})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['title'] = 'Creación de Planta'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': company.id})
        context['action'] = 'add'
        context['entity'] = 'Creación de Planta'
        context['div'] = '8'
        context['icon'] = 'bi bi-building-fill-add'
        return context


# Edición de Planta
class SiteUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Site
    form_class = SiteUpdateForm
    template_name = 'site/create_site.html'
    permission_required = 'company.add_company'

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
        context = super().get_context_data(**kwargs)
        company = Company.objects.first()
        context['title'] = 'Edición de Planta'
        context['list_url'] = reverse_lazy('company:company_detail', kwargs={'pk': company.id})
        context['entity'] = 'Edición de Planta'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'bi bi-building-fill'
        return context


# Detalle de Planta
class SiteDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Site
    template_name = 'site/detail_site.html'
    permission_required = 'company.add_company'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Planta'
        context['entity'] = 'Planta: ' + self.object.site_name
        context['subtitle'] = 'Información de la planta'
        context['back'] = reverse_lazy('company:company_detail', kwargs={'pk': self.object.company.id})
        context['div'] = '12'
        # Get all processes associated with this site
        context['processes'] = Process.objects.select_related('site').filter(site_id=self.object.id, enable_process=True)
        context['stages'] = Stage.objects.filter(
            enable_stage=True, process__site_id=self.object.id).order_by('stage_name')
        context['sample_point'] = SamplePoint.objects.filter(
            enable_point=True, stage__process__site_id=self.object.id).order_by('sample_point_name')
        return context
