import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Site
from core.models import BaseModel


# Reactivos
class Reagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_reagent = models.CharField(max_length=200, verbose_name='Descripción')
    code_reagent = models.CharField(max_length=20, verbose_name='Código')
    technical_sheet = models.FileField(
        upload_to='technical_sheet/%Y%m%d', verbose_name='Ficha Técnica', null=True, blank=True)
    enable_reagent = models.BooleanField(default=True, verbose_name='Habilitado')
    manufacturer = models.CharField(max_length=100, verbose_name='Fabricante', null=True, blank=True)
    site = models.ForeignKey(Site, verbose_name='Planta', on_delete=models.CASCADE)
    umb = models.CharField(max_length=15, verbose_name='UMB')

    def __str__(self):
        return str(self.description_reagent)

    class Meta:
        verbose_name = 'Reagent'
        verbose_name_plural = 'Reagents'
        db_table = 'Reagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(Reagent, self).save(*args, **kwargs)


# Inventario de Reactivos
class InventoryReagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reagent = models.ForeignKey(Reagent, verbose_name='Reactivo', on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50, verbose_name='N° Lote')
    date_expire = models.DateField(verbose_name='Fecha de Vencimiento', null=True, blank=True)
    quantity_lt = models.FloatField(verbose_name='Cantidad (L o Kg)')
    quantity_ml = models.FloatField(verbose_name='Cantidad (mL)')
    unit_measurement = models.CharField(max_length=4, verbose_name='Unidad de Medida', default='mL')
    reagent_liquid = models.BooleanField(default=True, verbose_name='Estado del Reactivo')

    def __str__(self):
        return str(self.batch_number)

    class Meta:
        verbose_name = 'InventoryReagent'
        verbose_name_plural = 'InventoryReagents'
        db_table = 'InventoryReagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if self.reagent_liquid:
            self.unit_measurement = 'mL'
        else:
            self.unit_measurement = 'Gr'
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(InventoryReagent, self).save(*args, **kwargs)


# Movimientos de Reactivos
class TransactionReagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reagent_inventory = models.ForeignKey(InventoryReagent, verbose_name='Reactivo', on_delete=models.CASCADE)
    date_transaction = models.DateField(verbose_name='Fecha')
    use_register = models.CharField(default=True)
    quantity = models.IntegerField(verbose_name='Cantidad')

    def __str__(self):
        return str(self.quantity)

    class Meta:
        verbose_name = 'TransactionReagent'
        verbose_name_plural = 'TransactionsReagent'
        db_table = 'TransactionReagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if not self.user_creation:
                self.user_creation = user
            else:
                self.user_updated = user
        return super(TransactionReagent, self).save(*args, **kwargs)

