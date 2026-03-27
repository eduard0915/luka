import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
from core.equipment.forms import CalibrationForm
from core.equipment.models import Calibration
from core.mixins import ValidatePermissionRequiredMixin
from luka import settings


# Listado de Calibraciones
class CalibrationListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Calibration
    template_name = 'calibration/list_calibration.html'
    permission_required = 'equipment.view_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                calibrations = list(Calibration.objects.select_related(
                    'equipment_instrumental',
                    'responsible_user'
                ).values(
                    'id',
                    'equipment_instrumental__code_equipment',
                    'equipment_instrumental__description_equipment',
                    'date_calibration',
                    'date_calibration_next',
                    'calibrated_by',
                    'parameter',
                    'comply',
                    'responsible_user__first_name',
                    'responsible_user__last_name',
                    'certificate_calibration',
                ).order_by('-date_calibration'))

                for c in calibrations:
                    first_name = c.get('responsible_user__first_name', '') or ''
                    last_name = c.get('responsible_user__last_name', '') or ''
                    code_eq = c.get('equipment_instrumental__code_equipment', '') or ''
                    description_eq = c.get('equipment_instrumental__description_equipment', '') or ''
                    c['equipment'] = f"{code_eq} - {description_eq}"
                    c['responsible_user__full_name'] = f"{first_name} {last_name}".strip()
                    c['has_file'] = bool(c.get('certificate_calibration'))

                return JsonResponse(calibrations, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Calibraciones'
        context['create_url'] = reverse_lazy('equipment:create_calibration')
        context['entity'] = 'Calibraciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-gauge-high'
        return context


# Creación de Calibración
class CalibrationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Calibration
    form_class = CalibrationForm
    template_name = 'calibration/create_calibration.html'
    permission_required = 'equipment.add_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = CalibrationForm(request.POST, request.FILES)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Calibración registrada satisfactoriamente!')
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
        return reverse('equipment:list_calibration')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Calibración'
        context['action'] = 'add'
        context['entity'] = 'Calibraciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-gauge-high'
        context['list_url'] = reverse_lazy('equipment:list_calibration')
        return context


# Edición de Calibración
class CalibrationUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Calibration
    form_class = CalibrationForm
    template_name = 'calibration/update_calibration.html'
    permission_required = 'equipment.change_calibration'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = CalibrationForm(request.POST, request.FILES, instance=self.object)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Calibración editada satisfactoriamente!')
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
        return reverse('equipment:list_calibration')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Calibración'
        context['entity'] = 'Editar Calibración'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-gauge-high'
        context['list_url'] = reverse_lazy('equipment:list_calibration')
        context['create_url'] = reverse_lazy('equipment:create_calibration')
        return context


# Detalle de Calibración
class CalibrationDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Calibration
    template_name = 'calibration/detail_calibration.html'
    permission_required = 'equipment.view_calibration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Calibración'
        context['entity'] = 'Detalle de Calibración'
        context['icon'] = 'fa-solid fa-gauge-high'
        context['list_url'] = reverse_lazy('equipment:list_calibration')
        context['update_url'] = reverse_lazy('equipment:update_calibration', kwargs={'pk': self.object.pk})
        context['pdf_url'] = reverse_lazy('equipment:calibration_pdf', kwargs={'pk': self.object.pk})
        return context


# Reporte PDF de Calibración
class CalibrationPDFView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'equipment.view_calibration'

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
            template = get_template('calibration/pdf_calibration.html')
            calibration = Calibration.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'calibration': calibration,
                'company': company,
                'title': f'Reporte de Calibración: {calibration.equipment_instrumental.code_equipment}',
                'today': timezone.now(),
            }

            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')

            pisa_status = pisa.CreatePDF(
                html,
                dest=response,
                link_callback=self.link_callback
            )

            if pisa_status.err:
                raise Exception('Error al generar el PDF')

            return response

        except Calibration.DoesNotExist:
            messages.error(request, 'La calibración no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('equipment:list_calibration'))
