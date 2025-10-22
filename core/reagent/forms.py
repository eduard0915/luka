from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput

from core.reagent.models import Reagent, TransactionReagent, InventoryReagent


UMB = [('', '-----'), ('mL', 'Mililitro'), ('g', 'Gramo')]
BOOLEAN = [('', '-----'), (True, 'Si'), (False, 'No')]
UNIT_PURITY = [('', '-----'), ('%', '%'), ('mg/L', 'mg/L')]
REGISTRY_TYPE = [('', '-----'), ('Uso', 'Uso'), ('Ajuste de Salida', 'Ajuste de Salida'), ('Ajuste de Entrada', 'Ajuste de Entrada')]


# Creación Reactivo
class ReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Reagent
        fields = [
            'code_reagent', 'description_reagent', 'umb', 'manufacturer', 'site', 'technical_sheet', 'purity_unit',
            'molecular_weight', 'gram_equivalent', 'stability_solution', 'volumetric', 'solvent']
        widgets = {
            'description_reagent': TextInput(attrs={'class': 'form-control', 'required': True}),
            'code_reagent': TextInput(attrs={'class': 'form-control', 'required': True}),
            'manufacturer': TextInput(attrs={'class': 'form-control', 'required': True}),
            'molecular_weight': TextInput(attrs={'class': 'form-control', 'required': True}),
            'gram_equivalent': TextInput(attrs={'class': 'form-control', 'required': True}),
            'stability_solution': TextInput(attrs={'class': 'form-control', 'required': True}),
            'technical_sheet': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'site': Select(attrs={'class': 'form-control', 'required': True}),
            'umb': Select(attrs={'class': 'form-control', 'required': True}, choices=UMB),
            'purity_unit': Select(attrs={'class': 'form-control', 'required': True}, choices=UNIT_PURITY),
            'volumetric': Select(attrs={'class': 'form-control', 'required': True}, choices=BOOLEAN),
            'solvent': Select(attrs={'class': 'form-control', 'required': True}, choices=BOOLEAN),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Registro de Entrada Inventario de Reactivo
class InventoryReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = InventoryReagent
        fields = ['reagent', 'quantity_stock', 'batch_number', 'date_expire', 'purity', 'certificate_quality']
        widgets = {
            'quantity_stock': TextInput(attrs={'class': 'form-control', 'required': True}),
            'purity': TextInput(attrs={'class': 'form-control', 'required': True}),
            'certificate_quality': FileInput(attrs={'class': 'form-control', 'required': True}),
            'reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'batch_number': TextInput(attrs={'class': 'form-control', 'required': True}),
            'date_expire': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de Registro de Entrada Inventario de Reactivo
class InventoryReagentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = InventoryReagent
        fields = ['reagent', 'quantity_stock','batch_number', 'date_expire']
        widgets = {
            'reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'quantity_stock': TextInput(attrs={'class': 'form-control', 'required': True}),
            'batch_number': TextInput(attrs={'class': 'form-control', 'required': True}),
            'date_expire': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación Transacción de Reactivo
class TransactionReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.invent = kwargs.pop('invent')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = TransactionReagent
        fields = ['reagent_inventory', 'date_transaction', 'quantity', 'type_transaction', 'detail_transaction']
        widgets = {
            'reagent_inventory': Select(attrs={'class': 'form-control', 'required': True}),
            'type_transaction': Select(attrs={'class': 'form-control', 'required': True}, choices=REGISTRY_TYPE),
            'date_transaction': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date'}),
            'quantity': NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
            'detail_transaction': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.reagent_inventory_id = self.invent.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Actualización Transacción de Reactivo
class TransactionReagentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = TransactionReagent
        fields = ['reagent_inventory', 'date_transaction']
        widgets = {
            'reagent_inventory': Select(attrs={'class': 'form-control', 'required': True}),
            'date_transaction': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date'}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
