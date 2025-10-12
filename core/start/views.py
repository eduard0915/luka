from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from core.user.models import Training


# Inicio
class StartView(LoginRequiredMixin, TemplateView):
    template_name = 'start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio'
        context['entity'] = 'Inicio'

        # Actualizar las capacitaciones vencidas
        now = timezone.now()
        Training.objects.filter(
            training_status='Vigente',
            date_training_expire__lte=now
        ).update(training_status='Vencido')

        return context


# Vista de no retorno por no permisos a una vista
class NotPermsView(TemplateView):
    template_name = 'notperms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sin Permisos de Acceso'
        return context

