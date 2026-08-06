"""Formularios de la aplicación de inicio de sesión.

Define el formulario de validación de correo electrónico para
la recuperación de contraseñas y el formulario de autenticación
con mensajes de error personalizados.
"""  # noqa: E501

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError

from core.user.models import User


class LoginAuthenticationForm(AuthenticationForm):
    """Formulario de autenticación con mensajes de error diferenciados
    para usuario inexistente y usuario inactivo."""

    error_messages = {
        'invalid_login': 'Usuario y/o Contraseña Incorrectos',
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                self.user_cache = User.objects.get_by_natural_key(username)
            except User.DoesNotExist:
                raise ValidationError(
                    'Usuario Inexistente',
                    code='invalid_login',
                )

            if not self.user_cache.is_active:
                raise ValidationError(
                    'Usuario Inactivo',
                    code='inactive',
                )

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )

        return self.cleaned_data


class EmailValidationForgotPassword(PasswordResetForm):
    """Formulario que valida la existencia del correo electrónico antes de enviar el enlace de restablecimiento."""

    def clean_email(self):
        """Verifica que el correo ingresado pertenezca a un usuario activo."""
        email_id = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email_id, is_active=True).exists():
            raise ValidationError("Email Invalido! Usuario Inactivo o Inexistente")
        return email_id

    def save(self, domain_override=None,
             subject_template_name='resetpwd_subject.txt',
             email_template_name='resetpwd_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """Envía el correo de restablecimiento de contraseña usando la plantilla HTML personalizada."""
        return super().save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            use_https=use_https,
            token_generator=token_generator,
            from_email=from_email,
            request=request,
            html_email_template_name='resetpwd_email.html',
            extra_email_context=extra_email_context,
        )
