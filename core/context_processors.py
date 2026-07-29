"""Context processors globales para las plantillas de Luka LIS.

Inyecta en el contexto de todas las plantillas la información de la
compañía y los contadores de alarmas, muestreos, mantenimientos y
calibraciones vencidas o pendientes.
"""
from django.db.models import Q
from django.utils import timezone

from core.company.models import Company
from core.equipment.models import Maintenance, Calibration, EquipmentInstrumental
from core.sampling.models import SamplingProcess, SamplingAnalysis
from core.user.models import Training


def extras_processor(request):
    """
    Context processor that adds company information to the context of all templates.
    Returns:
        dict: A dictionary containing company information.
    """
    context = {'count_total_alarm': 0}

    if request.user.is_authenticated:

        context['training_expire_count'] = Training.objects.filter(
            user__slug=request.user.slug, training_status='Vencido').count()

        user_site = getattr(getattr(request.user, 'laboratory', None), 'site', None)

        if user_site is not None:
            site_sampling_filter = (
                Q(group_sampling__sampling_point__product__site=user_site) |
                Q(point_sampling__product__site=user_site)
            )

            equipment = EquipmentInstrumental.objects.filter(
                enable_equipment=True, laboratory__site=user_site).count()
            sampling_day = SamplingProcess.objects.filter(
                date_sampling__date=timezone.localdate()).filter(site_sampling_filter).count()

            context['count_scheduled_sampling'] = SamplingProcess.objects.filter(
                status_sampling='Programada').filter(site_sampling_filter).count()
            context['count_confirmed_sampling'] = SamplingProcess.objects.filter(
                status_sampling='Confirmada').filter(site_sampling_filter).count()
            context['count_in_process_sampling'] = SamplingProcess.objects.filter(
                status_sampling='En Proceso').filter(site_sampling_filter).count()
            context['count_sampling_end'] = SamplingProcess.objects.filter(
                status_sampling__in=['Aprobado', 'Rechazado']).filter(site_sampling_filter).count()

            context['count_oos_result'] = SamplingAnalysis.objects.filter(comply='No Cumple').filter(
                Q(sampling_process__group_sampling__sampling_point__product__site=user_site) |
                Q(sampling_process__point_sampling__product__site=user_site)
            ).count()

            context['count_mtto_expire'] = Maintenance.objects.filter(
                next_date_maintenance__lt=timezone.localtime(),
                maintenance_next_completed=False,
                equipment_instrumental__laboratory__site=user_site).count()

            context['count_mtto_expire_responsible'] = Maintenance.objects.filter(
                next_date_maintenance__lt=timezone.localtime(),
                responsible_user__slug=request.user.slug,
                maintenance_next_completed=False,
                equipment_instrumental__laboratory__site=user_site).count()

            context['count_calibration_expire'] = Calibration.objects.filter(
                date_calibration_next__lt=timezone.localtime(),
                equipment_instrumental__laboratory__site=user_site).count()

            context['count_calibration_expire_responsible'] = Calibration.objects.filter(
                date_calibration_next__lt=timezone.localtime(),
                responsible_user__slug=request.user.slug,
                equipment_instrumental__laboratory__site=user_site).count()
        else:
            equipment = 0
            sampling_day = 0
            context['count_scheduled_sampling'] = 0
            context['count_confirmed_sampling'] = 0
            context['count_in_process_sampling'] = 0
            context['count_sampling_end'] = 0
            context['count_oos_result'] = 0
            context['count_mtto_expire'] = 0
            context['count_mtto_expire_responsible'] = 0
            context['count_calibration_expire'] = 0
            context['count_calibration_expire_responsible'] = 0
        context['count_total_alarm'] = context['training_expire_count'] + context[
            'count_calibration_expire_responsible'] + context['count_mtto_expire_responsible']

        context['percent_expire_mtto'] = round((context['count_mtto_expire'] / equipment) * 100, 2) if equipment > 0 else 0
        context['percent_expire_calibration'] = round((context['count_calibration_expire'] / equipment) * 100, 2) if equipment > 0 else 0

        sampling_scheduled_confirmed_total = context['count_confirmed_sampling'] + context['count_scheduled_sampling']
        if sampling_day > 0:
            context['percent_sampling_scheduled'] = round((context['count_scheduled_sampling'] / sampling_day) * 100, 2)
        elif sampling_scheduled_confirmed_total > 0:
            context['percent_sampling_scheduled'] = round((context['count_scheduled_sampling'] / sampling_scheduled_confirmed_total) * 100, 2)
        else:
            context['percent_sampling_scheduled'] = 0

        context['percent_sampling_confirmed'] = round((context['count_confirmed_sampling'] / sampling_scheduled_confirmed_total) * 100, 2) if sampling_scheduled_confirmed_total > 0 else 0

        if sampling_day > 0:
            context['percent_sampling_end'] = round((context['count_sampling_end'] / sampling_day) * 100, 2)
        elif context['count_in_process_sampling'] > 0:
            context['percent_sampling_end'] = round((context['count_sampling_end'] / context['count_in_process_sampling']) * 100, 2)
        else:
            context['percent_sampling_end'] = 0

        context['percent_oos_result'] = round((context['count_oos_result'] / context['count_in_process_sampling']) * 100, 2) if context['count_in_process_sampling'] > 0 else 0

        try:
            company = Company.objects.first()
            context['company'] = company
        except Exception:
            pass

    return context
