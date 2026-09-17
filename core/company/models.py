"""Modelos de datos para la gestión de empresas, plantas y procesos del LIMS.

Define las entidades Company (empresa), Site (planta) y Process (proceso)
con sus respectivas relaciones y metadatos.
"""

import uuid

from django.db import models

from core.validators import validator_file_image
from luka.settings import MEDIA_URL, STATIC_URL


class Company(models.Model):
    """Representa una empresa dentro del sistema LIMS.

    Almacena la información general de la empresa incluyendo nombre, NIT,
    dirección, ciudad, país, logotipo, configuración de alertas de capacitación,
    muestreo automático, habilitación de servicio y notificaciones por correo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    company_name = models.CharField(default='Nombre Empresa', max_length=120, verbose_name='Nombre Empresa')
    company_logo = models.ImageField(
        upload_to='company', null=True, blank=True, verbose_name='Logo', validators=[validator_file_image])
    company_nit = models.CharField(default='0000000000-0', max_length=20, verbose_name='NIT')
    company_address = models.CharField(default='Direccion', max_length=60, verbose_name='Dirección')
    company_city = models.CharField(default='Ciudad', max_length=60, verbose_name='Ciudad')
    company_country = models.CharField(default='Pais', max_length=60, verbose_name='Pais')
    training_alert = models.PositiveSmallIntegerField(default=30, verbose_name='Alerta Capacitaciones')
    autosample = models.BooleanField(default=True, verbose_name='Muestreo Automático')
    service_software = models.BooleanField(default=True, verbose_name='Servicio Habilitado')
    notification_email = models.BooleanField(default=True, verbose_name='Notificaciones por Email')

    def __str__(self):
        """Retorna el nombre de la empresa como representación en cadena."""
        return str(self.company_name)

    def get_logo(self):
        """Retorna la URL del logotipo de la empresa o una imagen por defecto si no existe."""
        if self.company_logo:
            return '{}{}'.format(MEDIA_URL, self.company_logo)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        db_table = 'Company'


class Site(models.Model):
    """Representa una planta o sitio perteneciente a una empresa.

    Almacena la información de ubicación de la planta (nombre, dirección,
    ciudad, país) y su relación con la empresa a la que pertenece.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    site_name = models.CharField(max_length=120, verbose_name='Planta')
    site_address = models.CharField(max_length=60, verbose_name='Dirección')
    site_city = models.CharField(max_length=60, verbose_name='Ciudad')
    site_country = models.CharField(max_length=60, verbose_name='País')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='')
    site_enable = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        """Retorna el nombre de la planta como representación en cadena."""
        return str(self.site_name)

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
        db_table = 'Site'


class Process(models.Model):
    """Representa un proceso asociado a una planta dentro del LIMS.

    Cada proceso pertenece a una planta específica y puede ser habilitado
    o deshabilitado según se requiera en el flujo de trabajo del laboratorio.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    process_name = models.CharField(max_length=120, verbose_name='Proceso')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Planta')
    enable_process = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        """Retorna el nombre del proceso como representación en cadena."""
        return str(self.process_name)

    class Meta:
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'
        db_table = 'Process'
