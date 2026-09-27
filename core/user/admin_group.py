"""Administración del modelo Group con exportación e importación de permisos.

Agrega al panel de administración de "Grupos de usuario" la opción de
descargar un Excel con los permisos de cada grupo (una pestaña por grupo) y de
importar un Excel con el mismo formato para crear o actualizar los grupos.
"""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from core.user.services import (
    apply_group_permissions,
    build_group_permissions_workbook,
    parse_group_permissions_workbook,
)

EXCEL_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class GroupAdmin(BaseGroupAdmin):
    """Administración de grupos de usuario con exportación e importación de permisos."""

    def get_urls(self):
        """Registra las rutas para exportar e importar permisos de grupos."""
        urls = [
            path(
                'export-permissions/',
                self.admin_site.admin_view(self.export_permissions_view),
                name='auth_group_export_permissions',
            ),
            path(
                'import-permissions/',
                self.admin_site.admin_view(self.import_permissions_view),
                name='auth_group_import_permissions',
            ),
        ]
        return urls + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        """Inyecta en el contexto si el usuario puede exportar e importar permisos."""
        extra_context = extra_context or {}
        extra_context['can_export_group_permissions'] = self.has_view_permission(request)
        extra_context['can_import_group_permissions'] = self.has_change_permission(request)
        return super().changelist_view(request, extra_context)

    def export_permissions_view(self, request):
        """Genera y descarga el Excel con los permisos de todos los grupos."""
        if not self.has_view_permission(request):
            raise PermissionDenied

        workbook = build_group_permissions_workbook()
        response = HttpResponse(content_type=EXCEL_CONTENT_TYPE)
        filename = f'permisos_grupos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        workbook.save(response)
        return response

    def import_permissions_view(self, request):
        """Muestra el formulario de importación y procesa el Excel cargado."""
        if not self.has_change_permission(request):
            raise PermissionDenied

        changelist_url = reverse('admin:auth_group_changelist')

        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                self.message_user(request, 'Debe seleccionar un archivo Excel (.xlsx).', messages.ERROR)
                return HttpResponseRedirect(changelist_url)
            try:
                parsed_groups = parse_group_permissions_workbook(excel_file)
                result = apply_group_permissions(parsed_groups)
            except ValueError as exc:
                self.message_user(request, str(exc), messages.ERROR)
            except Exception as exc:
                self.message_user(request, f'Error al importar los permisos: {exc}', messages.ERROR)
            else:
                self.message_user(
                    request,
                    f'Importación completada: {result["created"]} grupo(s) creado(s) y '
                    f'{result["updated"]} actualizado(s).',
                    messages.SUCCESS,
                )
                for warning in result['warnings'][:10]:
                    self.message_user(request, warning, messages.WARNING)
            return HttpResponseRedirect(changelist_url)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Importar permisos de grupos de usuario',
        }
        return TemplateResponse(request, 'admin/auth/group/import_group_permissions.html', context)
