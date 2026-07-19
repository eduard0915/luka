from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select, SelectMultiple

from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation
from core.analytical_method.forms import UNIT_CALCULATE, POSITION
from core.product.models import SamplePoint, Product, AnalyticalMethodProduct, SpecificationProduct


FREQUENCY = [
    ('', 'No Aplica'),
    (4, '4'),
    (6, '6'),
    (8, '8'),
    (12, '12'),
    (24, '24'),
]

PERIODICITY = [
    ('Diaria', 'Diaria'),
    ('Semanal', 'Semanal'),
    ('Mensual', 'Mensual'),
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

SEQUENCE = [('', '')] + [(i, i) for i in range(1, 50)]


# Creación de Productos
class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'code_product': 'col-md-3',
            'description_product': 'col-md-6',
            'site': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-4')

    class Meta:
        model = Product
        fields = ['code_product', 'description_product', 'site']
        widgets = {
            'code_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site': Select(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        user = get_current_user()
        try:
            if form.is_valid():
                data = form.save()
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
        self.fields['specification'].queryset = SpecificationProduct.objects.select_related('product').filter(product=self.product)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'specification': 'col-md-12',
            'sample_type': 'col-md-5',
            'sequence': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-4')

    def clean(self):
        cleaned_data = super().clean()
        periodicity = cleaned_data.get('periodicity')
        sample_frequency = cleaned_data.get('sample_frequency')

        # Validar que si la periodicidad es Diaria, la frecuencia no puede estar vacía
        if periodicity == 'Diaria' and (sample_frequency is None or sample_frequency == ''):
            raise ValidationError({
                'sample_frequency': 'La frecuencia es obligatoria cuando la periodicidad es Diaria.'
            })

        return cleaned_data

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'periodicity', 'sequence', 'sample_type', 'sample_frequency', 'specification']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sample_type': Select(attrs={'class': 'form-control'}, choices=TYPE_SAMPLE),
            'periodicity': Select(attrs={'class': 'form-control'}, choices=PERIODICITY),
            'sequence': Select(attrs={'class': 'form-control', 'required': True}, choices=SEQUENCE),
            'specification': SelectMultiple(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.product_id = self.product.id
                data.save()
                # commit=False difiere el guardado del M2M; hay que persistirlo
                # explícitamente o las especificaciones seleccionadas se pierden.
                self.save_m2m()
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
        self.fields['specification'].queryset = SpecificationProduct.objects.filter(product=self.sample.product)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'specification': 'col-md-12',
            'sample_type': 'col-md-6',
            'sequence': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-4')

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence', 'sample_type', 'specification']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': Select(attrs={'class': 'form-control'}, choices=FREQUENCY),
            'sample_type': Select(attrs={'class': 'form-control'}, choices=TYPE_SAMPLE),
            'sequence': TextInput(attrs={'class': 'form-control', 'required': True}),
            'specification': SelectMultiple(attrs={'class': 'form-control', 'required': True}),
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


# Formularios para Cálculos Dependientes de Productos
class ProductCalculateRelationDescriptionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['calculate_description_relation', 'unit_measure_calculate']
        widgets = {
            'calculate_description_relation': TextInput(attrs={'class': 'form-control'}),
            'unit_measure_calculate': Select(attrs={'class': 'form-control'}, choices=UNIT_CALCULATE)
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


class ProductCalculateRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['analytical_method_calculate'].queryset = AnalyticalMethodCalculate.objects.exclude(
            calculate_description__isnull=True).exclude(calculate_description='').distinct()
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['analytical_method_calculate', 'position']
        widgets = {
            'analytical_method_calculate': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
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


class ProductVolumenStdRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['volumen_std', 'position']
        widgets = {
            'volumen_std': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
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


class ProductFactorRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['factor', 'position']
        widgets = {
            'factor': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
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


class ProductSampleGramRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['sample_quantity', 'position']
        widgets = {
            'sample_quantity': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
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
