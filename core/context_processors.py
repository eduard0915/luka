from core.company.models import Company
from core.user.models import Training


def extras_processor(request):
    """
    Context processor that adds company information to the context of all templates.
    
    Returns:
        dict: A dictionary containing company information.
    """
    context = {'count_total_alarm': 0}
    if request.user.is_authenticated:
        context['training_expire_count'] = Training.objects.filter(user=request.user, training_status='Vencido').count()
        context['count_total_alarm'] = context['training_expire_count']
        try:
            # Get the first company (assuming there's only one company in the system)
            company = Company.objects.first()
            return {
                'company': company,
            }
        except Exception as e:
            # Return an empty dict if there's an error or no company exists
            print(e)
            pass
    return context
