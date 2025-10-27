import uuid

from crum import get_current_user
from django.db import models

from core.company.models import Site
from core.models import BaseModel
from core.user.models import User


# Reactivos
class Reagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    description_reagent = models.CharField(max_length=200, verbose_name='Descripción')
    code_reagent = models.CharField(max_length=20, verbose_name='Código')
    technical_sheet = models.FileField(
        upload_to='technical_sheet/%Y%m%d', verbose_name='Ficha Técnica', null=True, blank=True)
    enable_reagent = models.BooleanField(default=True, verbose_name='Habilitado')
    manufacturer = models.CharField(max_length=100, verbose_name='Fabricante/Marca', null=True, blank=True)
    site = models.ForeignKey(Site, verbose_name='Planta', on_delete=models.CASCADE)
    umb = models.CharField(max_length=15, verbose_name='UMB')
    purity_unit = models.CharField(max_length=10, verbose_name='Unidad de Pureza')
    molecular_weight = models.FloatField(verbose_name='Gramos/mol')
    gram_equivalent = models.FloatField(verbose_name='Eq-gramo')
    stability_solution = models.PositiveSmallIntegerField(verbose_name='Días Estabilidad en Solución', null=True, blank=True)
    volumetric = models.BooleanField(default=False, verbose_name='Volumétrico')
    solvent = models.BooleanField(default=False, verbose_name='Solvente')
    density_enable = models.BooleanField(default=False, verbose_name='Densidad')

    def __str__(self):
        return str(self.code_reagent) + ' '  + str(self.description_reagent) + ' (' + str(self.umb) + ') - ' + 'Pureza: ' + str(self.purity_unit) + ''

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
    quantity_stock = models.FloatField(verbose_name='Cantidad')
    purity = models.FloatField(verbose_name='Pureza')
    certificate_quality = models.FileField(
        upload_to='certificate_quality/%Y%m%d', verbose_name='Certificado de Calidad', null=True, blank=True)
    density = models.FloatField(verbose_name='Densidad (g/mL)', default=1)

    def __str__(self):
        return str(self.reagent.description_reagent) + ' Lote N°: ' + str(self.batch_number) + ' (' + str(
            self.purity) + str(self.reagent.purity_unit) + '). Disponible: ' + str(
            self.quantity_stock) + self.reagent.umb

    class Meta:
        verbose_name = 'InventoryReagent'
        verbose_name_plural = 'InventoryReagents'
        db_table = 'InventoryReagent'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        user = get_current_user()
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
    type_transaction = models.CharField(max_length=50, verbose_name='Tipo de Registro')
    detail_transaction = models.CharField(max_length=250, verbose_name='Detalle de Registro')
    quantity = models.IntegerField(verbose_name='Cantidad')
    user_transaction = models.ForeignKey(User, verbose_name='', on_delete=models.CASCADE)

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
