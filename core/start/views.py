from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# Inicio
class StartView(LoginRequiredMixin, TemplateView):
    template_name = 'start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio'
        return context


# Vista de no retorno por no permisos a una vista
class NotPermsView(TemplateView):
    template_name = 'notperms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sin Permisos de Acceso'
        return context

