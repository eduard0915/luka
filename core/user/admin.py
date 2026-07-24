"""Configuración del panel de administración de Django para la aplicación de usuarios."""

from django.contrib import admin
from core.user.models import User


class UserAdmin(admin.ModelAdmin):
    """Configuración del modelo User en el panel de administración de Django."""

    search_fields = (
        'id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone', 'is_active', 'site'
    )
    list_display = (
        'id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone', 'is_active', 'site'
    )


# Register your models here.
admin.site.register(User, UserAdmin)
