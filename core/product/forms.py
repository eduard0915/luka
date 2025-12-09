from crum import get_current_user
from django.forms import ModelForm, TextInput, Select

from core.product.models import SamplePoint, Product


FREQUENCY = [
    ('', 'No Aplica'),
    (4, '4'),
    (6, '6'),
    (8, '8'),
    (24, 'Diario'),
    (720, 'Mensual'),
]

# Creación de Productos
class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Product
        fields = ['code_product', 'description_product']
        widgets = {
            'code_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_product': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        user = get_current_user()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.site_id = user.site.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación de Puntos de Muestreo
class SamplePointForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sequence': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.product_id = self.product.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de Puntos de Muestreo
class SamplePointUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sequence': TextInput(attrs={'class': 'form-control', 'required': True})
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
