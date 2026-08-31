"""Mixins de validación para vistas basadas en clases de Django.

Actualmente incluye ``ValidatePermissionRequiredMixin``, que verifica
que el usuario autenticado posea los permisos requeridos antes de
acceder a una vista.
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy


class ValidatePermissionRequiredMixin(object):
    """
    Mixin para validar permisos de usuario en vistas basadas en clases.
    """
    permission_required = ''
    url_redirect = None

    def get_perms(self):
        """Retorna una tupla con los permisos requeridos por la vista."""
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def get_url_redirect(self):
        """Retorna la URL a la que se redirige si el usuario no tiene permisos."""
        if self.url_redirect is None:
            return reverse_lazy('start:notperms')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de ejecutar la vista; redirige si no tiene acceso."""
        if request.user.has_perms(self.get_perms()):
            return super().dispatch(request, *args, **kwargs)
        return redirect(self.get_url_redirect())
