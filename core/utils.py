# Función para formatear errores
def format_form_errors(form):
    """
    Formatea los errores del formulario de manera legible.
    Retorna una cadena con el formato: "Campo: Mensaje de error"

    Args:
        form: Instancia del formulario de Django

    Returns:
        str: Cadena formateada con los errores
    """
    error_list = []

    for field_name, errors in form.errors.items():
        # Obtener el verbose_name del campo
        if field_name == '__all__':
            # Errores generales del formulario (no específicos de un campo)
            for error in errors:
                error_list.append(str(error))
        else:
            # Obtener el verbose_name del campo o usar el nombre del campo
            field = form.fields.get(field_name)
            if field and hasattr(field, 'label') and field.label:
                field_label = field.label
            elif hasattr(form.instance._meta.get_field(field_name), 'verbose_name'):
                field_label = form.instance._meta.get_field(field_name).verbose_name
            else:
                field_label = field_name.replace('_', ' ').capitalize()

            # Procesar cada error del campo
            for error in errors:
                error_list.append(f"{field_label}: {error}")

    return ' | '.join(error_list)
