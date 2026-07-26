"""Modelos de datos de la aplicación de reactivos para Luka LIMS.

Define los modelos Reagent, InventoryReagent y TransactionReagent junto con
el generador de códigos secuenciales para reactivos.
"""

import uuid

from crum import get_current_user
from django.db import models, transaction
from django.utils import timezone

from core.company.models import Site
from core.models import BaseModel
from core.user.models import User


def code_reagent_generator():
    """
    Genera el siguiente código secuencial de forma segura bloqueando la fila.
    Inicia en 1000001 y aumenta de 1 en 1.
    """
    last_reagent = Reagent.objects.select_for_update().filter(code_reagent__regex=r'^\d+$').order_by('-code_reagent').first()

    if not last_reagent:
        return "1000001"

    current_number = int(last_reagent.code_reagent)
    new_number = current_number + 1
    return str(new_number)


class Reagent(BaseModel):
    """Modelo que representa un reactivo químico en el laboratorio."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_reagent = models.CharField(max_length=200, verbose_name='Descripción')
    code_reagent = models.CharField(max_length=20, verbose_name='Código', unique=True, blank=True)
    technical_sheet = models.FileField(
        upload_to='technical_sheet/%Y%m%d', verbose_name='Ficha Técnica', null=True, blank=True)
    enable_reagent = models.BooleanField(default=True, verbose_name='Habilitado')
    manufacturer = models.CharField(max_length=100, verbose_name='Fabricante/Marca', null=True, blank=True)
    site = models.ForeignKey(Site, verbose_name='Planta', on_delete=models.CASCADE)
    umb = models.CharField(max_length=15, verbose_name='UMB')
    purity_unit = models.CharField(max_length=10, verbose_name='Unidad de Pureza')
    molecular_weight = models.FloatField(verbose_name='Gramos/mol')
    gram_equivalent = models.FloatField(verbose_name='Eq-gramo')
    volumetric = models.BooleanField(default=False, verbose_name='Uso Volumétrico?')
    solvent = models.BooleanField(default=False, verbose_name='Uso como Solvente?')
    density_enable = models.BooleanField(default=False, verbose_name='Usa Densidad?')
    sig_figs_solution = models.PositiveSmallIntegerField(default=2, verbose_name='Cifras Significativas')
    standard = models.BooleanField(default=False, verbose_name='Es Estándar?')
    ready_to_use = models.BooleanField(verbose_name='STD Listo para Usar?', default=False)

    def __str__(self):
        """Retorna una representación legible del reactivo con código y descripción."""
        return str(self.code_reagent) + ' '  + str(self.description_reagent)

    class Meta:
        verbose_name = 'Reagent'
        verbose_name_plural = 'Reagents'
        db_table = 'Reagent'

    def save(self, *args, **kwargs):
        """Guarda el reactivo asignando el usuario actual y generando el código automáticamente."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user

        if not self.code_reagent:
            with transaction.atomic(using=kwargs.get('using')):
                self.code_reagent = code_reagent_generator()
                return super(Reagent, self).save(*args, **kwargs)

        return super(Reagent, self).save(*args, **kwargs)


class InventoryReagent(BaseModel):
    """Modelo que representa el inventario de un reactivo con lote, pureza y cantidad disponible."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reagent = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50, verbose_name='N° Lote')
    date_expire = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_stock = models.FloatField(verbose_name='Cantidad')
    purity = models.FloatField(verbose_name='Pureza')
    certificate_quality = models.FileField(
        upload_to='certificate_quality/%Y%m%d', verbose_name='Certificado de Calidad', null=True, blank=True)
    density = models.FloatField(verbose_name='Densidad (g/mL)', default=1)

    def __str__(self):
        """Retorna una representación del inventario con descripción, lote, pureza y cantidad disponible."""
        return str(self.reagent.description_reagent) + ' Lote N°: ' + str(self.batch_number) + ' (' + str(
            self.purity) + str(self.reagent.purity_unit) + '). Disponible: ' + str(
            self.quantity_stock) + self.reagent.umb

    class Meta:
        verbose_name = 'InventoryReagent'
        verbose_name_plural = 'InventoryReagents'
        db_table = 'InventoryReagent'

    def save(self, *args, **kwargs):
        """Guarda el inventario asignando el usuario actual."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(InventoryReagent, self).save(*args, **kwargs)


class TransactionReagent(BaseModel):
    """Modelo que representa una transacción o movimiento de un reactivo en el inventario."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reagent_inventory = models.ForeignKey(InventoryReagent, verbose_name='Reactivo', on_delete=models.CASCADE)
    date_transaction = models.DateField(verbose_name='Fecha')
    type_transaction = models.CharField(max_length=50, verbose_name='Tipo de Registro')
    detail_transaction = models.CharField(max_length=250, verbose_name='Detalle de Registro')
    quantity = models.FloatField(verbose_name='Cantidad')
    user_transaction = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)

    def __str__(self):
        """Retorna la cantidad de la transacción como representación."""
        return str(self.quantity)

    class Meta:
        verbose_name = 'TransactionReagent'
        verbose_name_plural = 'TransactionsReagent'
        db_table = 'TransactionReagent'

    def save(self, *args, **kwargs):
        """Guarda la transacción asignando el usuario actual."""
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(TransactionReagent, self).save(*args, **kwargs)
