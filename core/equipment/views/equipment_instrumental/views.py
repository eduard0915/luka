"""Vistas de equipos instrumentales para la gestión del inventario de equipos del laboratorio."""

import os
from datetime import date

from dateutil.relativedelta import relativedelta
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
from core.equipment.forms import EquipmentInstrumentalForm
from core.equipment.models import EquipmentInstrumental
from core.mixins import ValidatePermissionRequiredMixin
from luka import settings


class EquipmentInstrumentalCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista de creación de equipos instrumentales."""

    model = EquipmentInstrumental
    form_class = EquipmentInstrumentalForm
    template_name = 'equipment_instrumental/create_equipment.html'
    permission_required = 'equipment.add_equipmentinstrumental'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP inicializando el objeto como nulo."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud POST para registrar un nuevo equipo instrumental."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code_equipment = form.cleaned_data.get('code_equipment')
                    messages.success(request, f'Equipo "{code_equipment}" creado satisfactoriamente!')
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
        """Retorna la URL de redirección después de crear un equipo instrumental."""
        return reverse('equipment:list_equipment_instrumental')

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de creación."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Equipo Instrumental'
        context['action'] = 'add'
        context['entity'] = 'Equipos Instrumentales'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-microscope'
        context['list_url'] = reverse_lazy('equipment:list_equipment_instrumental')
        return context


class EquipmentInstrumentalListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista de listado de equipos instrumentales."""

    model = EquipmentInstrumental
    template_name = 'equipment_instrumental/list_equipment.html'
    permission_required = 'equipment.view_equipmentinstrumental'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP aplicando la exención de CSRF."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa las solicitudes POST para la búsqueda y listado de equipos instrumentales."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                equipments = list(EquipmentInstrumental.objects.select_related(
                    'laboratory',
                    'laboratory__site',
                    'responsible_user'
                ).values(
                    'id',
                    'code_equipment',
                    'description_equipment',
                    'brand_equipment',
                    'model_equipment',
                    'serie_equipment',
                    'laboratory__laboratory_name',
                    'laboratory__site__site_name',
                    'date_start_use',
                    'date_disabled',
                    'time_use',
                    'responsible_user__first_name',
                    'responsible_user__last_name',
                    'enable_equipment'
                ).filter(laboratory=request.user.laboratory).order_by('code_equipment'))

                for equipment in equipments:
                    first_name = equipment.get('responsible_user__first_name', '') or ''
                    last_name = equipment.get('responsible_user__last_name', '') or ''
                    equipment['responsible_user__full_name'] = f"{first_name} {last_name}".strip()
                    equipment['enable_equipment_display'] = 'Sí' if equipment['enable_equipment'] else 'No'

                return JsonResponse(equipments, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def update_time_use_equipment(self):
        """Actualiza el tiempo de uso en años de los equipos restando la fecha de inicio de uso a la fecha actual."""
        today = date.today()
        equipments = list(
            EquipmentInstrumental.objects.exclude(date_start_use__isnull=True).only('id', 'time_use', 'date_start_use')
        )
        for equipment in equipments:
            delta = relativedelta(today, equipment.date_start_use)
            equipment.time_use = round(delta.years + delta.months / 12, 2)
        EquipmentInstrumental.objects.bulk_update(equipments, ['time_use'])

    def get(self, request, *args, **kwargs):
        """Atiende la solicitud GET actualizando el tiempo de uso antes de renderizar el listado."""
        self.update_time_use_equipment()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de listado."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Equipos Instrumentales'
        context['create_url'] = reverse_lazy('equipment:create_equipment_instrumental')
        context['entity'] = 'Equipos Instrumentales'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-microscope'
        return context


class EquipmentInstrumentalUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista de edición de equipos instrumentales."""

    model = EquipmentInstrumental
    form_class = EquipmentInstrumentalForm
    template_name = 'equipment_instrumental/update_equipment.html'
    permission_required = 'equipment.change_equipmentinstrumental'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP obteniendo el objeto a editar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud POST para actualizar un equipo instrumental existente."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code_equipment = form.cleaned_data.get('code_equipment')
                    messages.success(request, f'Equipo "{code_equipment}" editado satisfactoriamente!')
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
        """Retorna la URL de redirección después de editar un equipo instrumental."""
        return reverse('equipment:list_equipment_instrumental')

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto adicionales para la plantilla de edición."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Equipo Instrumental'
        context['entity'] = 'Editar Equipo Instrumental'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-microscope'
        context['list_url'] = reverse_lazy('equipment:list_equipment_instrumental')
        return context


class EquipmentInstrumentalDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista de detalle u hoja de vida de equipo instrumental."""

    model = EquipmentInstrumental
    template_name = 'equipment_instrumental/detail_equipment.html'
    permission_required = 'equipment.add_equipmentinstrumental'
    queryset = EquipmentInstrumental.objects.select_related('laboratory__site', 'responsible_user')

    def dispatch(self, request, *args, **kwargs):
        """Dispacha la solicitud HTTP."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega datos de contexto incluyendo mantenimientos, calibraciones, verificaciones y patrones asociados."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hoja de Vida de Equipo Instrumental'
        context['entity'] = 'Hoja de Vida de Equipo Instrumental'
        context['icon'] = 'fa-solid fa-microscope'
        context['list_url'] = reverse_lazy('equipment:list_equipment_instrumental')
        context['update_url'] = reverse_lazy('equipment:update_equipment_instrumental', kwargs={'pk': self.object.pk})
        context['maintenances'] = self.object.maintenance_set.select_related('responsible_user').all().order_by('-date_maintenance')
        context['calibrations'] = self.object.calibration_set.select_related('responsible_user').all().order_by('-date_calibration')
        context['verifications'] = self.object.verification_set.select_related('responsible_user').all().order_by('-date_verification')
        context['reference_patterns'] = self.object.referencepattern_set.all().order_by('description_pattern')
        context['pdf_url'] = reverse('equipment:equipment_instrumental_pdf', kwargs={'pk': self.object.pk})
        return context


class EquipmentInstrumentalPDFView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista de generación de reporte PDF de hoja de vida de equipo instrumental."""

    permission_required = 'equipment.view_equipmentinstrumental'

    @staticmethod
    def link_callback(uri, rel):
        """Convierte URIs HTML a rutas absolutas del sistema para que xhtml2pdf acceda a los recursos."""
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
        """Genera y retorna el reporte PDF de hoja de vida de un equipo instrumental específico."""
        try:
            template = get_template('equipment_instrumental/pdf_equipment.html')
            object = EquipmentInstrumental.objects.select_related('laboratory__site', 'responsible_user').get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'object': object,
                'maintenances': object.maintenance_set.select_related('responsible_user').all().order_by('-date_maintenance'),
                'calibrations': object.calibration_set.select_related('responsible_user').all().order_by('-date_calibration'),
                'verifications': object.verification_set.select_related('responsible_user').all().order_by('-date_verification'),
                'company': company,
                'title': f'Hoja de Vida de Equipo: {object.code_equipment}',
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

        except EquipmentInstrumental.DoesNotExist:
            messages.error(request, 'El equipo no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('equipment:list_equipment_instrumental'))
