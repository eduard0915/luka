import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from xhtml2pdf import pisa

from core.company.models import Company
from core.equipment.forms import MaintenanceForm
from core.equipment.models import Maintenance
from core.mixins import ValidatePermissionRequiredMixin
from luka import settings


# Listado de Mantenimientos
class MaintenanceListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Maintenance
    template_name = 'maintenance/list_maintenance.html'
    permission_required = 'equipment.view_maintenance'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                maintenances = list(Maintenance.objects.select_related(
                    'equipment_instrumental',
                    'responsible_user'
                ).values(
                    'id',
                    'equipment_instrumental__code_equipment',
                    'equipment_instrumental__description_equipment',
                    'date_maintenance',
                    'type_maintenance',
                    'maintenance_by',
                    'responsible_user__first_name',
                    'responsible_user__last_name',
                    'file_maintenance',
                ).order_by('-date_maintenance'))

                for m in maintenances:
                    first_name = m.get('responsible_user__first_name', '') or ''
                    last_name = m.get('responsible_user__last_name', '') or ''
                    m['responsible_user__full_name'] = f"{first_name} {last_name}".strip()
                    m['has_file'] = bool(m.get('file_maintenance'))

                return JsonResponse(maintenances, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Mantenimientos'
        context['create_url'] = reverse_lazy('equipment:create_maintenance')
        context['entity'] = 'Mantenimientos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-tools'
        return context


# Creación de Mantenimiento
class MaintenanceCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/create_maintenance.html'
    permission_required = 'equipment.add_maintenance'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = MaintenanceForm(request.POST, request.FILES)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Mantenimiento registrado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
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
        return reverse('equipment:list_maintenance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Mantenimiento'
        context['action'] = 'add'
        context['entity'] = 'Mantenimientos'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-tools'
        context['list_url'] = reverse_lazy('equipment:list_maintenance')
        return context


# Edición de Mantenimiento
class MaintenanceUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/update_maintenance.html'
    permission_required = 'equipment.change_maintenance'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = MaintenanceForm(request.POST, request.FILES, instance=self.object)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Mantenimiento editado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
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
        return reverse('equipment:list_maintenance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Mantenimiento'
        context['entity'] = 'Editar Mantenimiento'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-tools'
        context['list_url'] = reverse_lazy('equipment:list_maintenance')
        context['create_url'] = reverse_lazy('equipment:create_maintenance')
        return context


# Detalle de Mantenimiento
class MaintenanceDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Maintenance
    template_name = 'maintenance/detail_maintenance.html'
    permission_required = 'equipment.view_maintenance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Mantenimiento'
        context['entity'] = 'Detalle de Mantenimiento'
        context['icon'] = 'fa-solid fa-tools'
        context['list_url'] = reverse_lazy('equipment:list_maintenance')
        context['update_url'] = reverse_lazy('equipment:update_maintenance', kwargs={'pk': self.object.pk})
        context['pdf_url'] = reverse_lazy('equipment:maintenance_pdf', kwargs={'pk': self.object.pk})
        return context


# Reporte PDF de Mantenimiento
class MaintenancePDFView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'equipment.view_maintenance'

    @staticmethod
    def link_callback(uri, rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        if not os.path.isfile(path):
            return None
        return path

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('maintenance/pdf_maintenance.html')
            maintenance = Maintenance.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'maintenance': maintenance,
                'company': company,
                'title': f'Reporte de Mantenimiento: {maintenance.equipment_instrumental.code_equipment}',
                'today': timezone.now(),
            }

            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = f'attachment; filename="maintenance_{maintenance.id}.pdf"'

            pisa_status = pisa.CreatePDF(
                html,
                dest=response,
                link_callback=self.link_callback
            )

            if pisa_status.err:
                raise Exception('Error al generar el PDF')

            return response

        except Maintenance.DoesNotExist:
            messages.error(request, 'El mantenimiento no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('equipment:list_maintenance'))
