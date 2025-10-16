from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput

from core.reagent.models import Reagent, TransactionReagent, InventoryReagent


TYPE_REAGENT = [(True, 'Liquido'), (False, 'Sólido')]
UMB = [('', '-----'), ('Mililitro', 'Mililitro'), ('Gramo', 'Gramo')]


# Creación Reactivo
class ReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Reagent
        fields = ['code_reagent', 'description_reagent', 'umb', 'manufacturer', 'site', 'technical_sheet']
        widgets = {
            'description_reagent': TextInput(attrs={'class': 'form-control', 'required': True}),
            'code_reagent': TextInput(attrs={'class': 'form-control', 'required': True}),
            'manufacturer': TextInput(attrs={'class': 'form-control', 'required': True}),
            'technical_sheet': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'site': Select(attrs={'class': 'form-control', 'required': True}),
            'umb': Select(attrs={'class': 'form-control', 'required': True}, choices=UMB),
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

# Creación Inventario de Reactivo
class InventoryReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = InventoryReagent
        fields = ['reagent', 'batch_number', 'date_expire', 'quantity_lt', 'reagent_liquid']
        widgets = {
            'reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'batch_number': TextInput(attrs={'class': 'form-control', 'required': True}),
            'date_expire': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity_lt': NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
            'reagent_liquid': Select(attrs={'class': 'form-control'}, choices=TYPE_REAGENT),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.quantity_ml = data.quantity_lt * 1000
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Actualización Inventario de Reactivo
class InventoryReagentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = InventoryReagent
        fields = ['reagent', 'batch_number', 'date_expire', 'quantity_lt',  'reagent_liquid']
        widgets = {
            'reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'batch_number': TextInput(attrs={'class': 'form-control', 'required': True}),
            'date_expire': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity_lt': NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
            'reagent_liquid': Select(attrs={'class': 'form-control'}, choices=TYPE_REAGENT),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.quantity_ml = data.quantity_lt * 1000
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación Transacción de Reactivo
class TransactionReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = TransactionReagent
        fields = ['reagent_inventory', 'date_transaction', 'use_register', 'quantity']
        widgets = {
            'reagent_inventory': Select(attrs={'class': 'form-control', 'required': True}),
            'date_transaction': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date'}),
            'use_register': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'quantity': NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
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


# Actualización Transacción de Reactivo
class TransactionReagentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = TransactionReagent
        fields = ['reagent_inventory', 'date_transaction', 'use_register', 'quantity']
        widgets = {
            'reagent_inventory': Select(attrs={'class': 'form-control', 'required': True}),
            'date_transaction': DateInput(attrs={'class': 'form-control', 'required': True, 'type': 'date'}),
            'use_register': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'quantity': NumberInput(attrs={'class': 'form-control', 'required': True, 'min': '0'}),
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
