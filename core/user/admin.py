"""Configuración del panel de administración de Django para la aplicación de usuarios."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from core.user.admin_group import GroupAdmin
from core.user.models import Competence, PasswordHistoryUser, Training, User


class UserAdmin(BaseUserAdmin):
    """Configuración del modelo User en el panel de administración de Django."""

    list_display = (
        'id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone', 'is_active', 'laboratory'
    )
    search_fields = (
        'id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone',
        'laboratory__laboratory_name'
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'cedula', 'cargo', 'email_person', 'cellphone', 'address_user', 'date_birth', 'photo',
                'laboratory', 'notification_email_oss',
            ),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('cedula', 'cargo', 'email_person', 'cellphone', 'address_user', 'date_birth', 'laboratory'),
        }),
    )


class PasswordHistoryUserAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo PasswordHistoryUser."""

    list_display = ('id', 'username', 'pass_date')
    list_filter = ('pass_date',)
    search_fields = ('id', 'username__username')


class CompetenceAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Competence."""

    list_display = ('id', 'description_competence', 'user', 'institution', 'date_competence')
    list_filter = ('institution', 'date_competence')
    search_fields = ('id', 'description_competence', 'institution', 'user__username')


class TrainingAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Training."""

    list_display = ('id', 'description_training', 'user', 'training_by', 'date_training', 'date_training_expire',
                    'training_status')
    list_filter = ('training_status', 'date_training', 'date_training_expire')
    search_fields = ('id', 'description_training', 'training_by', 'user__username')


admin.site.register(User, UserAdmin)
admin.site.register(PasswordHistoryUser, PasswordHistoryUserAdmin)
admin.site.register(Competence, CompetenceAdmin)
admin.site.register(Training, TrainingAdmin)

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, GroupAdmin)
