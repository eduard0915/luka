import uuid
from django.db import models
from core.user.models import User
from core.laboratory.models import Laboratory
from core.models import BaseModel
from crum import get_current_user


class Condition(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, verbose_name='Laboratorio', null=True, blank=True)
    area = models.CharField(max_length=150, verbose_name='Área')
    variable = models.CharField(max_length=150, verbose_name='Variable')
    upper_limit = models.FloatField(verbose_name='Límite Superior')
    lower_limit = models.FloatField(verbose_name='Límite Inferior')
    enabled = models.BooleanField(default=True, verbose_name='Habilitado')

    def __str__(self):
        return f"{self.area} - {self.variable}"

    class Meta:
        verbose_name = 'Condición'
        verbose_name_plural = 'Condiciones'
        db_table = 'Condition'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Condition, self).save(*args, **kwargs)


class ConditionRegister(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    registration_date = models.DateTimeField(verbose_name='Fecha de Registro')
    registered_by = models.ForeignKey(User, verbose_name='Registrado por', on_delete=models.CASCADE,
                                      related_name='registered_by_conditions')
    registered_data = models.FloatField(verbose_name='Dato Registrado')
    condition = models.ForeignKey(Condition, verbose_name='Área', on_delete=models.CASCADE)
    actions = models.TextField(verbose_name='Acciones', null=True, blank=True)
    actions_registered_by = models.ForeignKey(User, verbose_name='Acciones Registradas por', on_delete=models.CASCADE,
                                              related_name='actions_registered_by_conditions', null=True, blank=True)

    def __str__(self):
        return f"{self.condition} - {self.registration_date}"

    class Meta:
        verbose_name = 'Registro de Condición'
        verbose_name_plural = 'Registros de Condiciones'
        db_table = 'ConditionRegister'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(ConditionRegister, self).save(*args, **kwargs)
