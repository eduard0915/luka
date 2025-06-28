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


# Listado de Plantas
class SiteListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Site
    template_name = 'site/list_site.html'
    permission_required = 'company.add_company'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                list_site = list(Site.objects.values(
                    'id', 'site_name', 'site_address', 'site_city', 'site_country', 'site_enable').order_by('site_name'))
                return JsonResponse(list_site, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Plantas'
        context['create_url'] = reverse_lazy('company:create_site')
        context['entity'] = 'Plantas'
        context['div'] = '10'
        context['icon'] = 'factory'
        return context


# Creación de Planta
class SiteCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Site
    form_class = SiteForm
    template_name = 'site/create_site.html'
    success_url = reverse_lazy('company:list_site')
    permission_required = 'company.add_company'
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
                    messages.success(request, f'Planta creada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
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
        context['title'] = 'Creación de Planta'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Planta'
        context['div'] = '8'
        context['icon'] = 'factory'
        return context


# Edición de Planta
class SiteUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Site
    form_class = SiteUpdateForm
    template_name = 'site/create_site.html'
    success_url = reverse_lazy('company:list_site')
    permission_required = 'company.add_company'
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
        context['title'] = 'Edición de Planta'
        context['list_url'] = self.success_url
        context['entity'] = 'Edición de Planta'
        context['action'] = 'edit'
        context['div'] = '8'
        context['icon'] = 'factory'
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
        context['entity'] = 'Detalle de Planta'
        context['subtitle'] = 'Información de la planta'
        context['div'] = '12'
        # Get all processes associated with this site
        context['processes'] = Process.objects.select_related('site').filter(site_id=self.object.id, enable_process=True)
        context['stages'] = Stage.objects.filter(
            enable_stage=True, process__site_id=self.object.id).order_by('stage_name')
        context['sample_point'] = SamplePoint.objects.filter(
            enable_point=True, stage__process__site_id=self.object.id).order_by('sample_point_name')
        return context
