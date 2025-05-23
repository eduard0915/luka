from django.views.generic import TemplateView


# inicio
class HomeView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Luka Lims'
        return context
