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
from core.equipment.forms import VerificationForm
from core.equipment.models import Verification
from core.mixins import ValidatePermissionRequiredMixin
from luka import settings


# Listado de Verificaciones
class VerificationListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Verification
    template_name = 'verification/list_verification.html'
    permission_required = 'equipment.view_verification'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                verifications = list(Verification.objects.select_related(
                    'equipment_instrumental',
                    'responsible_user'
                ).values(
                    'id',
                    'equipment_instrumental__code_equipment',
                    'equipment_instrumental__description_equipment',
                    'date_verification',
                    'date_verification_next',
                    'verified_by',
                    'parameter_verified',
                    'comply',
                    'responsible_user__first_name',
                    'responsible_user__last_name',
                    'report_verification',
                ).order_by('-date_verification'))

                for v in verifications:
                    first_name = v.get('responsible_user__first_name', '') or ''
                    last_name = v.get('responsible_user__last_name', '') or ''
                    code_eq = v.get('equipment_instrumental__code_equipment', '') or ''
                    description_eq = v.get('equipment_instrumental__description_equipment', '') or ''
                    v['equipment'] = f"{code_eq} - {description_eq}"
                    v['responsible_user__full_name'] = f"{first_name} {last_name}".strip()
                    v['has_file'] = bool(v.get('report_verification'))

                return JsonResponse(verifications, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Verificaciones'
        context['create_url'] = reverse_lazy('equipment:create_verification')
        context['entity'] = 'Verificaciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-check-double'
        return context


# Creación de Verificación
class VerificationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Verification
    form_class = VerificationForm
    template_name = 'verification/create_verification.html'
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
                form = VerificationForm(request.POST, request.FILES)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Verificación registrada satisfactoriamente!')
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
        return reverse('equipment:list_verification')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de Verificación'
        context['action'] = 'add'
        context['entity'] = 'Verificaciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-check-double'
        context['list_url'] = reverse_lazy('equipment:list_verification')
        return context


# Edición de Verificación
class VerificationUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Verification
    form_class = VerificationForm
    template_name = 'verification/update_verification.html'
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
                form = VerificationForm(request.POST, request.FILES, instance=self.object)
                if form.is_valid():
                    self.object = form.save()
                    messages.success(request, f'Verificación editada satisfactoriamente!')
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
        return reverse('equipment:list_verification')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Verificación'
        context['entity'] = 'Editar Verificación'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-check-double'
        context['list_url'] = reverse_lazy('equipment:list_verification')
        context['create_url'] = reverse_lazy('equipment:create_verification')
        return context


# Detalle de Verificación
class VerificationDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Verification
    template_name = 'verification/detail_verification.html'
    permission_required = 'equipment.view_verification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Verificación'
        context['entity'] = 'Detalle de Verificación'
        context['icon'] = 'fa-solid fa-check-double'
        context['list_url'] = reverse_lazy('equipment:list_verification')
        context['update_url'] = reverse_lazy('equipment:update_verification', kwargs={'pk': self.object.pk})
        context['pdf_url'] = reverse_lazy('equipment:verification_pdf', kwargs={'pk': self.object.pk})
        return context


# Reporte PDF de Verificación
class VerificationPDFView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'equipment.view_verification'

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
            template = get_template('verification/pdf_verification.html')
            verification = Verification.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'verification': verification,
                'company': company,
                'title': f'Reporte de Verificación: {verification.equipment_instrumental.code_equipment}',
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

        except Verification.DoesNotExist:
            messages.error(request, 'La verificación no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('equipment:list_verification'))
