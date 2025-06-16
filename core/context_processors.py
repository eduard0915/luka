from core.company.models import Company

def extras_processor(request):
    """
    Context processor that adds company information to the context of all templates.
    
    Returns:
        dict: A dictionary containing company information.
    """
    try:
        # Get the first company (assuming there's only one company in the system)
        company = Company.objects.first()
        return {
            'company': company,
        }
    except Exception:
        # Return an empty dict if there's an error or no company exists
        return {}