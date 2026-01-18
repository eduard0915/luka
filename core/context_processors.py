from core.company.models import Company
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
        context['training_expire_count'] = Training.objects.filter(user__slug=request.user.slug, training_status='Vencido').count()
        context['count_scheduled_sampling'] = SamplingProcess.objects.filter(status_sampling='Programada').count()
        context['count_confirmed_sampling'] = SamplingProcess.objects.filter(status_sampling='Confirmada').count()
        context['count_in_process_sampling'] = SamplingProcess.objects.filter(status_sampling='En Proceso').count()
        context['count_total_alarm'] = context['training_expire_count']
        try:
            company = Company.objects.first()
            context['company'] = company
        except Exception:
            pass
    return context
