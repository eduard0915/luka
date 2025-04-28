from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError

from core.user.models import User


class EmailValidationForgotPassword(PasswordResetForm):

    def clean_email(self):
        email_id = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email_id, is_active=True).exists():
            raise ValidationError("Email Invalido! Usuario Inactivo o Inexistente")
        return email_id
