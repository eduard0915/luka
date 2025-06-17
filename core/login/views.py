from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.views import *
from django.shortcuts import redirect
from django.utils import timezone

from core.user.models import PasswordHistoryUser


# Login para iniciar sesión
class LoginFormView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        return context
