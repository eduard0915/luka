"""Vistas de la aplicación de inicio.

Define la vista principal de bienvenida al sistema.
"""  # noqa: E501

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Vista de la página de inicio del sistema PadLIMS."""

    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        """Agrega el título 'PadLIMS' al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'PadLIMS'
        return context
