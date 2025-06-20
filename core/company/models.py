import uuid

from django.db import models

from core.validators import validator_file_image
from luka.settings import MEDIA_URL, STATIC_URL


# Empresa
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    company_name = models.CharField(default='Nombre Empresa', max_length=120, verbose_name='Nombre Empresa')
    company_logo = models.ImageField(
        upload_to='company', null=True, blank=True, verbose_name='Logo', validators=[validator_file_image])
    company_nit = models.CharField(default='0000000000-0', max_length=20, verbose_name='NIT')
    company_address = models.CharField(default='Direccion', max_length=60, verbose_name='Dirección')
    company_city = models.CharField(default='Ciudad', max_length=60, verbose_name='Ciudad')
    company_country = models.CharField(default='Pais', max_length=60, verbose_name='Pais')

    def __str__(self):
        return str(self.company_name)

    def get_logo(self):
        if self.company_logo:
            return '{}{}'.format(MEDIA_URL, self.company_logo)
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        db_table = 'Company'


# Plantas
class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    site_name = models.CharField(max_length=120, verbose_name='Planta')
    site_address = models.CharField(max_length=60, verbose_name='Dirección')
    site_city = models.CharField(max_length=60, verbose_name='Ciudad')
    site_country = models.CharField(max_length=60, verbose_name='País')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='')
    site_enable = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.site_name)

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
        db_table = 'Site'


# Procesos
class Process(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    process_name = models.CharField(max_length=120, verbose_name='Proceso')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Planta')
    enable_process = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.process_name)

    class Meta:
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'
        db_table = 'Process'


# Etapas
class Stage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    stage_name = models.CharField(max_length=100, verbose_name='Etapa')
    stage_code = models.CharField(max_length=20, verbose_name='Codigo/Abreviación')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name='Proceso')
    enable_stage = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.stage_name)

    class Meta:
        verbose_name = 'Stage'
        verbose_name_plural = 'Stages'
        db_table = 'Stage'


# Puntos de Muestreo
class SamplePoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sample_point_name = models.CharField(max_length=100, verbose_name='Punto de Muestreo')
    sample_point_code = models.CharField(max_length=30, verbose_name='Codigo/Abreviación')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, verbose_name='Etapa')
    enable_point = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return str(self.sample_point_name)

    class Meta:
        verbose_name = 'SamplePoint'
        verbose_name_plural = 'SamplePoints'
        db_table = 'SamplePoint'
