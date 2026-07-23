from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, LoginView
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from core.company.models import Company
from core.user.models import PasswordHistoryUser
from luka import settings


# Restablecimiento de contraseña
class FormResetPasswordView(PasswordResetView):
    template_name = 'resetpwd_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Restablecer Contraseña'
        return context


class ResetPasswordDoneView(PasswordResetDoneView):
    template_name = 'resetpwd_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Correo Enviado'
        return context


class ResetConfirmPasswordView(PasswordResetConfirmView):
    template_name = 'resetpwd_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nueva Contraseña'
        return context


class ResetCompletePasswordView(PasswordResetCompleteView):
    template_name = 'resetpwd_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contraseña Restablecida'
        return context


# Login para iniciar sesión
class LoginFormView(LoginView):
    """Vista de inicio de sesión que valida la expiración de la contraseña del usuario autenticado."""
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        company = Company.objects.first()
        if company and not company.service_software:
            return redirect('service_not_available')
        if self.request.user.is_authenticated:
            username = self.request.user.id
            password = self.request.user.password
            password_history = PasswordHistoryUser.objects.filter(username_id=username, old_pass=password)
            time_password = int(settings.TIME_PASSWORD_EXPIRE) / 30
            for pw in password_history:
                expire_time_password = pw.pass_date + timedelta(days=int(settings.TIME_PASSWORD_EXPIRE))
                if timezone.now() > expire_time_password:
                    messages.warning(
                        request,
                        f'Su contraseña tiene más de {time_password} meses, realice actualización de su contraseña, debe ser diferente a las 3 últimas utilizadas')
                    return redirect('user:change_password')
                else:
                    return redirect(settings.LOGIN_REDIRECT_URL)
        return super(LoginFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega el título 'Iniciar sesión' al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        return context


class ServiceNotAvailableView(TemplateView):
    """Vista que muestra un mensaje de servicio no disponible.

    Cuando el campo service_software de la compañía está deshabilitado,
    redirige a esta vista para informar al usuario que el servicio no
    está disponible y proporciona el contacto de soporte técnico.
    """
    template_name = 'service_not_available.html'

    def get_context_data(self, **kwargs):
        """Agrega el título 'Servicio No Disponible' al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Servicio No Disponible'
        return context
