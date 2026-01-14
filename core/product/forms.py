from crum import get_current_user
from django.forms import ModelForm, TextInput, Select, SelectMultiple

from core.analytical_method.models import AnalyticalMethod
from core.product.models import SamplePoint, Product, AnalyticalMethodProduct, SpecificationProduct


FREQUENCY = [
    ('', 'No Aplica'),
    (4, '4'),
    (6, '6'),
    (8, '8'),
    (24, 'Diario'),
    (720, 'Mensual'),
]

UM = [
    ('', '----'),
    ('% p/p', '% p/p'),
    ('% p/v', '% p/v'),
    ('M', 'M'),
    ('N', 'N'),
    ('mg/L', 'mg/L'),
    ('ppm', 'ppm'),
    ('ppb', 'ppb'),
]

TYPE_TEST = [('Rango', 'Rango'), ('Descriptivo', 'Descriptivo')]

TYPE_SAMPLE = [('En Proceso', 'En Proceso'), ('Producto Terminado', 'Producto Terminado')]


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
        self.fields['method_analytical'].queryset = AnalyticalMethodProduct.objects.select_related('product').filter(product=self.product)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'method_analytical': 'col-md-12',
            'sample_type': 'col-md-6',
            'sequence': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-4')

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence', 'sample_type', 'method_analytical']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sample_type': Select(attrs={'class': 'form-control'}, choices=TYPE_SAMPLE),
            'sequence': TextInput(attrs={'class': 'form-control', 'required': True}),
            'method_analytical': SelectMultiple(attrs={'class': 'form-control', 'required': True})
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
        self.sample = kwargs.pop('sample')
        super().__init__(*args, **kwargs)
        self.fields['method_analytical'].queryset = AnalyticalMethodProduct.objects.filter(product=self.sample.product)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'method_analytical': 'col-md-12',
            'sample_type': 'col-md-6',
            'sequence': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-4')

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence', 'sample_type', 'method_analytical']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sample_type': Select(attrs={'class': 'form-control'}, choices=TYPE_SAMPLE),
            'sequence': TextInput(attrs={'class': 'form-control', 'required': True}),
            'method_analytical': SelectMultiple(attrs={'class': 'form-control', 'required': True}),
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


# Creación de Especificación de Producto
class SpecificationProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if self.product:
            self.fields['method_test'].queryset = AnalyticalMethodProduct.objects.filter(product=self.product)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'type_test': 'col-md-4',
            'test_prod': 'col-md-8',
            'lower_limit_prod': 'col-md-4',
            'upper_limit_prod': 'col-md-4',
            'features_prod': 'col-md-12',
            'method_test': 'col-md-12',
            'unit_measure': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SpecificationProduct
        fields = ['type_test', 'test_prod', 'lower_limit_prod', 'upper_limit_prod', 'unit_measure', 'features_prod','method_test']
        widgets = {
            'method_test': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'type_test': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=TYPE_TEST),
            'unit_measure': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=UM),
            'lower_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
            'upper_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['analytical_method'].queryset = AnalyticalMethod.objects.filter(enable_analytical_method=True)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodProduct
        fields = ['analytical_method']
        widgets = {
            'analytical_method': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
