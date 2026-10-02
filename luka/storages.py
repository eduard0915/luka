"""Backends de almacenamiento del proyecto.

Define el storage de S3 para archivos media, almacenados bajo el prefijo
``media/`` del bucket configurado y servidos a través de CloudFront cuando
``MEDIA_URL`` apunta a un dominio absoluto.
"""

from urllib.parse import urlparse

from decouple import config
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStore(S3Boto3Storage):
    """Storage de archivos media en S3 bajo el prefijo ``media/``."""

    location = 'media'
    default_acl = None
    file_overwrite = False
    region_name = config('REGION_NAME')
    custom_domain = urlparse(
        config('MEDIA_URL', default='') or config('MEDIA', default='')
    ).netloc or None
