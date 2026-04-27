from django.utils import timezone

from core.company.models import Company
from core.equipment.models import Maintenance, Calibration, EquipmentInstrumental
from core.sampling.models import SamplingProcess
from core.user.models import Training


def extras_processor(request):
    """
    Context processor that adds company information to the context of all templates.
    Returns:
        dict: A dictionary containing company information.
    """
    context = {'count_total_alarm': 0}

    if request.user.is_authenticated:

        equipment = EquipmentInstrumental.objects.filter(enable_equipment=True).count()
        sampling_day = SamplingProcess.objects.filter(date_sampling__date=timezone.localdate()).count()

        context['training_expire_count'] = Training.objects.filter(user__slug=request.user.slug, training_status='Vencido').count()
        context['count_scheduled_sampling'] = SamplingProcess.objects.filter(status_sampling='Programada').count()
        context['count_confirmed_sampling'] = SamplingProcess.objects.filter(status_sampling='Confirmada').count()
        context['count_in_process_sampling'] = SamplingProcess.objects.filter(status_sampling='En Proceso').count()
        context['count_mtto_expire'] = Maintenance.objects.filter(next_date_maintenance__lt=timezone.localtime(), maintenance_next_completed=False).count()
        context['count_mtto_expire_responsible'] = Maintenance.objects.select_related('responsible_user').filter(next_date_maintenance__lt=timezone.localtime(), responsible_user__slug=request.user.slug, maintenance_next_completed=False).count()
        context['count_calibration_expire'] = Calibration.objects.filter(date_calibration_next__lt=timezone.localtime()).count()
        context['count_calibration_expire_responsible'] = Calibration.objects.select_related('responsible_user').filter(date_calibration_next__lt=timezone.localtime(), responsible_user__slug=request.user.slug).count()
        context['count_total_alarm'] = context['training_expire_count'] + context['count_calibration_expire_responsible'] + context['count_mtto_expire_responsible']
        context['percent_expire_mtto'] = round((context['count_mtto_expire'] / equipment) * 100, 2) if equipment > 0 else 0
        context['percent_expire_calibration'] = round((context['count_calibration_expire'] / equipment) * 100, 2) if equipment > 0 else 0
        context['percent_sampling_scheduled'] = round((context['count_scheduled_sampling'] / sampling_day) * 100, 2) if sampling_day > 0 else 0

        try:
            company = Company.objects.first()
            context['company'] = company
        except Exception:
            pass

    return context
