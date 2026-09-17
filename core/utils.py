"""Utilidades compartidas para toda la aplicación Luka LIS.

Incluye funciones auxiliares como el formateo legible de errores
de formularios de Django.
"""

import math


def round_sig_figs(value, sig_figs=4):
    """
    Redondea un valor a n cifras significativas.

    A diferencia de round(), que redondea a n decimales, ajusta el número
    de decimales según el orden de magnitud del valor: 0.003333 con 2
    cifras significativas es 0.0033 (no 0.0), y 1234.5 con 2 es 1200.

    Args:
        value: Valor numérico a redondear
        sig_figs: Número de cifras significativas (default 4 si es vacío o <= 0)

    Returns:
        float: Valor redondeado a las cifras significativas indicadas
    """
    value = float(value)
    if value == 0:
        return 0.0
    sig_figs = int(sig_figs) if sig_figs and int(sig_figs) > 0 else 4
    decimals = sig_figs - 1 - math.floor(math.log10(abs(value)))
    return round(value, int(decimals))


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
