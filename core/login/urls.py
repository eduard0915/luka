from django.urls import path
from django.contrib.auth.views import LogoutView

from core.login.forms import EmailValidationForgotPassword
from core.login.views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    path('service-not-available/', ServiceNotAvailableView.as_view(), name='service_not_available'),
    path("logout/", LogoutView.as_view(), name='logout'),
    # path('login-failed/', lockout, name='login-failed'),
    path('reset/password_reset/', FormResetPasswordView.as_view(form_class=EmailValidationForgotPassword),
         name='password_reset'),
    path('reset/password_done/', ResetPasswordDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ResetConfirmPasswordView.as_view(), name='password_reset_confirm'),
    path('reset/done/', ResetCompletePasswordView.as_view(), name='password_reset_complete'),
]
