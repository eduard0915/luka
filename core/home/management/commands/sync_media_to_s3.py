"""Comando de administración para subir los archivos locales de MEDIA_ROOT a S3.

Los archivos se suben al bucket configurado conservando la ruta relativa y con
el prefijo ``media/``, que es el mismo que usa ``luka.storages.MediaStore``.
"""

import mimetypes
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from decouple import config
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Sube a S3 todos los archivos encontrados en MEDIA_ROOT."""

    help = 'Sube los archivos locales de MEDIA_ROOT al bucket S3 bajo el prefijo media/'

    def add_arguments(self, parser):
        """Configura los argumentos opcionales del comando."""
        parser.add_argument('--dry-run', action='store_true', help='Reporta lo que se subiría sin escribir en S3')
        parser.add_argument('--overwrite', action='store_true', help='Sobrescribe los objetos que ya existen en S3')
        parser.add_argument('--prefix', default='', help='Limita la sincronización a una subcarpeta de MEDIA_ROOT')

    def handle(self, *args, **options):
        """Recorre MEDIA_ROOT y sube cada archivo al bucket configurado."""
        if not settings.MEDIA_ROOT or not os.path.isdir(settings.MEDIA_ROOT):
            raise CommandError(f'MEDIA_ROOT no existe o no es un directorio: {settings.MEDIA_ROOT}')

        media_root = os.path.abspath(settings.MEDIA_ROOT)
        source_root = os.path.abspath(os.path.join(media_root, options['prefix']))
        if not source_root.startswith(media_root):
            raise CommandError('--prefix no puede salir de MEDIA_ROOT')
        if not os.path.isdir(source_root):
            raise CommandError(f'La ruta no existe: {source_root}')

        dry_run = options['dry_run']
        overwrite = options['overwrite']
        bucket = config('BUCKET')
        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4', region_name=config('REGION_NAME')))

        uploaded = 0
        skipped = 0
        errors = 0

        for dirpath, _, filenames in os.walk(source_root):
            for filename in sorted(filenames):
                local_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(local_path, media_root).replace(os.sep, '/')
                key = 'media/' + relative_path
                try:
                    if not overwrite and self._exists(s3, bucket, key):
                        skipped += 1
                        self.stdout.write(f'Ya existe, se omite: {key}')
                        continue
                    if dry_run:
                        uploaded += 1
                        self.stdout.write(f'[dry-run] Subiría: {key}')
                        continue
                    s3.upload_file(local_path, bucket, key, ExtraArgs=self._extra_args(local_path))
                    uploaded += 1
                    self.stdout.write(f'Subido: {key}')
                except (ClientError, OSError) as exc:
                    errors += 1
                    self.stderr.write(f'Error subiendo {key}: {exc}')

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{prefix}Subidos: {uploaded} | Omitidos: {skipped} | Errores: {errors}'))

    @staticmethod
    def _exists(s3, bucket, key):
        """Retorna True si el objeto ya existe en el bucket."""
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as exc:
            if exc.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                return False
            raise

    @staticmethod
    def _extra_args(local_path):
        """Detecta el ContentType del archivo para que S3/CloudFront lo sirva correctamente."""
        content_type, encoding = mimetypes.guess_type(local_path)
        extra_args = {'ContentType': content_type or 'application/octet-stream'}
        if encoding:
            extra_args['ContentEncoding'] = encoding
        return extra_args
