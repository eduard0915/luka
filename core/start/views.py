"""Vistas de la aplicación de inicio (start).

Define la vista principal posterior al inicio de sesión y la vista
de acceso denegado por falta de permisos.
"""  # noqa: E501

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from core.user.models import Training


class StartView(LoginRequiredMixin, TemplateView):
    """Vista de bienvenida principal del sistema después del inicio de sesión."""

    template_name = 'start.html'

    def get_context_data(self, **kwargs):
        """Agrega el título al contexto y actualiza automáticamente las capacitaciones vencidas."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio'
        context['entity'] = 'Inicio'

        now = timezone.now()
        Training.objects.filter(
            training_status='Vigente',
            date_training_expire__lte=now
        ).update(training_status='Vencido')

        return context


class NotPermsView(TemplateView):
    """Vista que se muestra cuando un usuario no tiene permisos para acceder a un recurso."""

    template_name = 'notperms.html'

    def get_context_data(self, **kwargs):
        """Agrega el título 'Sin Permisos de Acceso' al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sin Permisos de Acceso'
        return context

