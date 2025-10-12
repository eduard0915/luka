import os
import re

from django.core.exceptions import ValidationError


# Validador tamaño de archivos de 256Kb
def validator_file_image(value):
    limit = 256 * 1024     # de bits
    ext = os.path.splitext(value.name)[1]
    file = os.path.basename(value.name)
    namefile = os.path.splitext(file)[0]
    special_character = re.fullmatch('[A-Za-z0-9_!-]+', namefile)
    valid_extensions = ['.jpeg', '.jpg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Subir imagenes solamente con extensión .jpg, .png o .svg y tamaño máximo de 256Kb')
    if value.size > limit:
        raise ValidationError('Archivo demasiado grande. El tamaño no debe exceder los 256Kb.')
    if not special_character:
        raise ValidationError('El nombre del archivo debe ser alfanumérico sin caracteres especiales #@.,!*')


# Validador tamaño de imágenes de 256Kb
def validator_file_image_user(value):
    limit = 256 * 1024     # de bits
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpeg', '.jpg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Subir imágenes solamente con extensión .jpg, .png o .svg y tamaño máximo de 256Kb')
    if value.size > limit:
        raise ValidationError('Archivo demasiado grande. El tamaño no debe exceder los 256Kb.')
