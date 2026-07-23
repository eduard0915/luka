from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError

from core.user.models import User


class EmailValidationForgotPassword(PasswordResetForm):

    def clean_email(self):
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
