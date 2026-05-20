import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from xhtml2pdf import pisa

from core.company.models import Company
from core.equipment.forms import DailyVerificationForm
from core.equipment.models import DailyVerification, EquipmentInstrumental
from core.mixins import ValidatePermissionRequiredMixin
from luka import settings

from django.conf import settings
from django.contrib.staticfiles import finders


# Listado de Verificaciones Diarias
class DailyVerificationListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = DailyVerification
    template_name = 'daily_verification/list_daily_verification.html'
    permission_required = 'equipment.view_verification'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                verifications = list(DailyVerification.objects.select_related(
                    'equipment_instrumental',
                    'verified_by'
                ).values(
                    'id',
                    'equipment_instrumental__code_equipment',
                    'equipment_instrumental__description_equipment',
                    'equipment_instrumental__tolerance',
                    'equipment_instrumental__unit_tolerance',
                    'date_verification_daily',
                    'parameter_verified',
                    'comply',
                    'reference_pattern_daily',
                    'verified_by__first_name',
                    'verified_by__last_name',
                    'verification_result_daily',
                    'error'
                ).order_by('-date_verification_daily'))

                for v in verifications:
                    first_name = v.get('verified_by__first_name', '') or ''
                    last_name = v.get('verified_by__last_name', '') or ''
                    code_eq = v.get('equipment_instrumental__code_equipment', '') or ''
                    description_eq = v.get('equipment_instrumental__description_equipment', '') or ''
                    v['equipment'] = f"{code_eq} - {description_eq}"
                    v['verified_by__full_name'] = f"{first_name} {last_name}".strip()
                    if v['date_verification_daily']:
                        v['date_verification_daily'] = v['date_verification_daily'].strftime('%Y-%m-%d %H:%M')

                return JsonResponse(verifications, safe=False)
            elif action == 'get_graph_data':
                from datetime import timedelta
                twelve_months_ago = timezone.now() - timedelta(days=365)
                equipment_id = request.POST.get('equipment_id')
                qs = DailyVerification.objects.filter(date_verification_daily__gte=twelve_months_ago)
                if equipment_id:
                    qs = qs.filter(equipment_instrumental_id=equipment_id)
                qs = qs.order_by('date_verification_daily')
                
                data = {
                    'categories': [],
                    'series': [
                        {
                            'name': 'Error',
                            'data': [],
                            'units': []
                        },
                        {
                            'name': 'Tolerancia',
                            'data': [],
                            'units': []
                        },
                        {
                            'name': 'Tolerancia Negativa',
                            'data': [],
                            'units': []
                        }
                    ],
                    'unit_tolerance': '',
                    'min_y': 0,
                    'max_y': 0
                }

                if equipment_id:
                    equipment = EquipmentInstrumental.objects.filter(id=equipment_id).first()
                    if equipment:
                        data['unit_tolerance'] = equipment.unit_tolerance
                        tolerance = float(equipment.tolerance) if equipment.tolerance else 0.0
                        data['max_y'] = round(tolerance * 1.1, 2)
                        data['min_y'] = round(-tolerance * 1.1, 2)
                
                for v in qs:
                    unit = v.equipment_instrumental.unit_tolerance or ""
                    tolerance = float(v.equipment_instrumental.tolerance) if v.equipment_instrumental.tolerance else 0.0
                    data['categories'].append(v.date_verification_daily.strftime('%Y-%m-%d %H:%M'))
                    data['series'][0]['data'].append(float(v.error) if v.error else 0.0)
                    data['series'][0]['units'].append(unit)
                    data['series'][1]['data'].append(tolerance)
                    data['series'][1]['units'].append(unit)
                    data['series'][2]['data'].append(-tolerance)
                    data['series'][2]['units'].append(unit)
                
                return JsonResponse(data, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Verificaciones Diarias'
        context['create_url'] = reverse_lazy('equipment:create_daily_verification')
        context['entity'] = 'Verificaciones Diarias'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-calendar-check'
        return context


# Gráfico de Verificaciones Diarias
class DailyVerificationChartView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = DailyVerification
    template_name = 'daily_verification/chart_daily_verification.html'
    permission_required = 'equipment.view_verification'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'get_graph_data':
                data = {
                    'categories': [],
                    'series': [
                        {
                            'name': 'Error',
                            'data': []
                        },
                        {
                            'name': 'Tolerancia',
                            'data': []
                        },
                        {
                            'name': 'Tolerancia Negativa',
                            'data': []
                        }
                    ],
                    'min_y': 0,
                    'max_y': 0,
                    'unit_tolerance': ''
                }

                # Filtrar por equipo si se pasa un ID
                equipment_id = self.kwargs.get('pk')
                equipment = None
                qs = DailyVerification.objects.all()
                if equipment_id:
                    equipment = EquipmentInstrumental.objects.filter(id=equipment_id).first()
                    if equipment:
                        data['unit_tolerance'] = equipment.unit_tolerance
                        tolerance = float(equipment.tolerance) if equipment.tolerance else 0.0
                        data['max_y'] = round(tolerance * 1.1, 2)
                        data['min_y'] = round(-tolerance * 1.1, 2)
                    qs = qs.select_related('equipment_instrumental').filter(equipment_instrumental_id=equipment_id)

                qs = qs.order_by('date_verification_daily')
                for v in qs:
                    tolerance = float(v.equipment_instrumental.tolerance) if v.equipment_instrumental.tolerance else 0.0
                    data['categories'].append(v.date_verification_daily.strftime('%Y-%m-%d %H:%M'))
                    data['series'][0]['data'].append(float(v.error) if v.error else 0.0)
                    data['series'][1]['data'].append(tolerance)
                    data['series'][2]['data'].append(-tolerance)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gráfico de Verificaciones Diarias'

        equipment_id = self.kwargs.get('pk')
        if equipment_id:
            equipment = EquipmentInstrumental.objects.filter(id=equipment_id).first()
            if equipment:
                context['title'] = f'Gráfico de Verificaciones Diarias - {equipment.code_equipment}'
                context['entity'] = f'Gráfico de Verificaciones Diarias - {equipment.code_equipment} {equipment.description_equipment}'
        context['back'] = reverse_lazy('equipment:list_equipment_instrumental')
        context['icon'] = 'fa-solid fa-chart-line'
        return context


# Creación de Verificación Diaria
class DailyVerificationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = DailyVerification
    form_class = DailyVerificationForm
    template_name = 'daily_verification/create_daily_verification.html'
    permission_required = 'equipment.add_verification'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = DailyVerificationForm(request.POST)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Verificación diaria registrada satisfactoriamente!')
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
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_success_url(self):
        return reverse_lazy('equipment:list_daily_verification')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva Verificación Diaria'
        context['entity'] = 'Verificaciones Diarias'
        context['list_url'] = reverse_lazy('equipment:list_daily_verification')
        context['action'] = 'add'
        context['icon'] = 'fa-solid fa-calendar-plus'
        return context


# Actualización de Verificación Diaria
class DailyVerificationUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = DailyVerification
    form_class = DailyVerificationForm
    template_name = 'daily_verification/create_daily_verification.html'
    permission_required = 'equipment.change_verification'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = DailyVerificationForm(request.POST, instance=self.object)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Verificación diaria actualizada satisfactoriamente!')
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
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_success_url(self):
        return reverse_lazy('equipment:list_daily_verification')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Verificación Diaria'
        context['entity'] = 'Verificaciones Diarias'
        context['list_url'] = reverse_lazy('equipment:list_daily_verification')
        context['action'] = 'edit'
        context['icon'] = 'fa-solid fa-calendar-check'
        return context


# Detalle de Verificación Diaria
class DailyVerificationDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = DailyVerification
    template_name = 'daily_verification/detail_daily_verification.html'
    permission_required = 'equipment.view_verification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Verificación Diaria'
        context['entity'] = 'Verificaciones Diarias'
        context['list_url'] = reverse_lazy('equipment:list_daily_verification')
        context['update_url'] = reverse_lazy('equipment:update_daily_verification', kwargs={'pk': self.object.id})
        context['pdf_url'] = reverse_lazy('equipment:daily_verification_pdf', kwargs={'pk': self.object.id})
        context['icon'] = 'fa-solid fa-calendar-day'
        return context


# Vista PDF de Verificación Diaria
class DailyVerificationPDFView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'equipment.view_verification'

    def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        result = finders.find(uri)
        if result:
            if not isinstance(result, (list, tuple)):
                result = [result]
            result = list(os.path.realpath(path) for path in result)
            path = result[0]
        else:
            s_url = settings.STATIC_URL  # Typically /static/
            s_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
            m_url = settings.MEDIA_URL  # Typically /media/
            m_root = settings.MEDIA_ROOT  # Typically /home/userX/project_media/

            if uri.startswith(m_url):
                path = os.path.join(m_root, uri.replace(m_url, ""))
            elif uri.startswith(s_url):
                path = os.path.join(s_root, uri.replace(s_url, ""))
            else:
                return uri

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (s_url, m_url)
            )
        return path

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('daily_verification/pdf_daily_verification.html')
            context = {
                'verification': DailyVerification.objects.get(pk=self.kwargs['pk']),
                'company': Company.objects.first(),
                'today': timezone.now(),
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="daily_verification.pdf"'
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=DailyVerificationPDFView.link_callback
            )
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response
        except Exception as e:
            print(e)
            return HttpResponseRedirect(reverse_lazy('equipment:list_daily_verification'))
