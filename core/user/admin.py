from django.contrib import admin
from core.user.models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone', 'is_active')
    list_display = ('id', 'username', 'first_name', 'last_name', 'cargo', 'email', 'cedula', 'cellphone', 'is_active')


# Register your models here.
admin.site.register(User, UserAdmin)
