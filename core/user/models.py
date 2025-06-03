import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import localtime

from luka.settings import MEDIA_URL, STATIC_URL


def validator_file_image(value):
    limit = 256 * 1024     # de bits
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpeg', '.jpg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Subir imagenes solamente con extensión .jpg, .png o .svg y tamaño máximo de 256Kb')
    if value.size > limit:
        raise ValidationError('Archivo demasiado grande. El tamaño no debe exceder los 256Kb.')


# Usuarios
class User(AbstractUser):
    cedula = models.CharField(max_length=15, null=True, blank=True, unique=False, verbose_name='Cédula')
    cargo = models.CharField(max_length=50, null=True, blank=True, verbose_name='Cargo')
    email_person = models.EmailField(null=True, blank=True, verbose_name='Email Personal')
    cellphone = models.CharField(max_length=10, null=True, blank=True, verbose_name='N° Celular')
    address_user = models.CharField(max_length=50, null=True, blank=True, verbose_name='Dirección')
    date_birth = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    photo = models.ImageField(
        upload_to='user/%Y%m%d', null=True, blank=True, verbose_name='Foto', validators=[validator_file_image])
    slug = models.SlugField(unique=True, null=False, blank=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.original_password = self.password

    def __str__(self):
        return str(self.get_full_name()) + ', ' + str(self.cargo)

    def get_image(self):
        if self.photo:
            return '{}{}'.format(MEDIA_URL, self.photo)
        return '{}{}'.format(STATIC_URL, 'img/default-avatar.png')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(uuid.uuid4()))
        if self.username is not int:
            self.username = self.username.lower()
        if self.id:
            if self._password_has_been_changed():
                PasswordHistoryUser.remember_password(self)
        super().save(*args, **kwargs)

    def _password_has_been_changed(self):
        return self.original_password != self.password


# Histórico de Contraseñas utilizadas
class PasswordHistoryUser(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    old_pass = models.CharField(max_length=128)
    pass_date = models.DateTimeField()

    @classmethod
    def remember_password(cls, user):
        if user:
            cls(username=user, old_pass=user.password, pass_date=localtime()).save()


# Competencias
class Competence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_competence = models.CharField(max_length=200, verbose_name='Descripción')
    institution = models.CharField(max_length=200, verbose_name='Institución')
    date_competence = models.DateField(verbose_name='Fecha Certificación')
    support_competence = models.FileField(upload_to='competence/%Y%m%d', verbose_name='Soporte')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='')

    def __str__(self):
        return str(self.description_competence)

    class Meta:
        verbose_name = 'Competence'
        verbose_name_plural = 'Competences'
        db_table = 'Competence'


# Capacitaciones
class Training(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_training = models.CharField(max_length=120, verbose_name='Capacitación')
    training_by = models.CharField(max_length=200, verbose_name='Realizado por')
    date_training = models.DateField(verbose_name='Fecha')
    support_training = models.FileField(upload_to='support_training/%Y%m%d', verbose_name='Soporte')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='')

    def __str__(self):
        return str(self.description_training)

    class Meta:
        verbose_name = 'Training'
        verbose_name_plural = 'Trainings'
        db_table = 'Training'
