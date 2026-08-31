"""Formularios para la gestión de productos, puntos de muestreo,
especificaciones y métodos analíticos dentro del sistema PadLims.

Define las listas de opciones (frecuencia, periodicidad, unidades de medida,
tipo de ensayo, tipo de muestra y secuencia) y los formularios asociados
a cada modelo del módulo product.
"""

from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelChoiceField, TextInput, Select, SelectMultiple

from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation, OPERATION
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
    ('mg/Kg', 'mg/Kg'),
]

TYPE_TEST = [('Rango', 'Rango'), ('Descriptivo', 'Descriptivo')]

TYPE_SAMPLE = [('En Proceso', 'En Proceso'), ('Producto Terminado', 'Producto Terminado')]

SEQUENCE = [('', '')] + [(i, i) for i in range(1, 50)]


# Creación de Productos
class ProductForm(ModelForm):
    """Formulario para la creación y edición de productos."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario asignando clases CSS y desactivando autocompletado."""
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
        """Metadatos del formulario ProductForm."""
        model = Product
        fields = ['code_product', 'description_product', 'site']
        widgets = {
            'code_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site': Select(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        """Guarda el producto validando el formulario y retornando los datos o errores."""
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
    """Formulario para la creación de puntos de muestreo asociados a un producto."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando las especificaciones por producto."""
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
        """Valida que la frecuencia sea obligatoria cuando la periodicidad es Diaria."""
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
        """Metadatos del formulario SamplePointForm."""
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
        """Guarda el punto de muestreo asociándolo al producto y persistiendo las relaciones M2M."""
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
    """Formulario para la edición de puntos de muestreo existentes."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario cargando las especificaciones del producto asociado."""
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
        """Metadatos del formulario SamplePointUpdateForm."""
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
        """Guarda los cambios del punto de muestreo y retorna los datos o errores."""
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


# Asignación de Especificación de Producto
class SpecificationProductForm(ModelForm):
    """Formulario para la creación de especificaciones de producto con métodos analíticos."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los métodos analíticos por producto."""
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
        """Metadatos del formulario SpecificationProductForm."""
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
        """Guarda la especificación asignándole el producto correspondiente."""
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


# Edición de Asignación de Especificación de Producto
class SpecificationProductUpdateForm(ModelForm):
    """Formulario para la edición de especificaciones de producto existentes."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario cargando la especificación y filtrando los métodos disponibles."""
        self.spc = kwargs.pop('spc', None)
        super().__init__(*args, **kwargs)
        if self.spc:
            self.fields['method_test'].queryset = AnalyticalMethodProduct.objects.filter(product=self.spc.product)
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
        """Metadatos del formulario SpecificationProductUpdateForm."""
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
        """Guarda la especificación editada y retorna la instancia o los errores."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save()
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Asignación de Especificación de Producto desde Cálculo
class SpecificationProductCalculeForm(ModelForm):
    """Formulario para la creación de especificaciones basadas en cálculos relacionales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los métodos de cálculo relacional por producto."""
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['method_test_relacional'].queryset = AnalyticalMethodCalculateRelation.objects.filter(
            product=self.product).exclude(calculate_description_relation__in=[None, ''])
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'type_test': 'col-md-4',
            'test_prod': 'col-md-8',
            'lower_limit_prod': 'col-md-4',
            'upper_limit_prod': 'col-md-4',
            'features_prod': 'col-md-12',
            'method_test_relacional': 'col-md-12',
            'unit_measure': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        """Metadatos del formulario SpecificationProductCalculeForm."""
        model = SpecificationProduct
        fields = ['type_test', 'test_prod', 'lower_limit_prod', 'upper_limit_prod', 'unit_measure', 'features_prod','method_test_relacional']
        widgets = {
            'method_test_relacional': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'type_test': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=TYPE_TEST),
            'unit_measure': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=UM),
            'lower_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
            'upper_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        """Guarda la especificación por cálculo asignándole el producto correspondiente."""
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


# Edición de Asignación de Especificación de Producto desde Cálculo
class SpecificationProductCalculeUpdateForm(ModelForm):
    """Formulario para la edición de especificaciones basadas en cálculos relacionales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario cargando la especificación por cálculo y filtrando los métodos."""
        self.spc = kwargs.pop('spc', None)
        super().__init__(*args, **kwargs)
        self.fields['method_test_relacional'].queryset = AnalyticalMethodCalculateRelation.objects.filter(
            product=self.spc.product).exclude(calculate_description_relation__in=[None, ''])
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'type_test': 'col-md-4',
            'test_prod': 'col-md-8',
            'lower_limit_prod': 'col-md-4',
            'upper_limit_prod': 'col-md-4',
            'features_prod': 'col-md-12',
            'method_test_relacional': 'col-md-12',
            'unit_measure': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        """Metadatos del formulario SpecificationProductCalculeUpdateForm."""
        model = SpecificationProduct
        fields = ['type_test', 'test_prod', 'lower_limit_prod', 'upper_limit_prod', 'unit_measure', 'features_prod','method_test_relacional']
        widgets = {
            'method_test_relacional': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'type_test': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=TYPE_TEST),
            'unit_measure': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=UM),
            'lower_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
            'upper_limit_prod': TextInput(attrs={'class': 'form-control', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        """Guarda la especificación por cálculo editada y retorna la instancia o los errores."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save()
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodProductForm(ModelForm):
    """Formulario para la asignación de métodos analíticos a un producto."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los métodos analíticos habilitados."""
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['analytical_method'].queryset = AnalyticalMethod.objects.filter(enable_analytical_method=True)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario AnalyticalMethodProductForm."""
        model = AnalyticalMethodProduct
        fields = ['analytical_method']
        widgets = {
            'analytical_method': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        """Guarda la asignación del método analítico al producto."""
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
    """Formulario para la descripción de un cálculo relacional asociado a un producto."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de descripción de cálculo."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductCalculateRelationDescriptionForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['calculate_description_relation', 'unit_measure_calculate', 'sig_figs']
        widgets = {
            'calculate_description_relation': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sig_figs': TextInput(attrs={'class': 'form-control', 'required': True}),
            'unit_measure_calculate': Select(attrs={'class': 'form-control'}, choices=UNIT_CALCULATE)
        }

    def save(self, commit=True):
        """Guarda la descripción del cálculo relacional asignándole el producto y el consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Registro de variable con análisis previo
class ProductCalculateRelationForm(ModelForm):
    """Formulario para la asignación de un método de cálculo analítico a un producto."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los cálculos de los métodos asociados al producto."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        if self.product is None and self.instance and self.instance.pk:
            self.product = self.instance.product
        queryset = AnalyticalMethodCalculate.objects.filter(
            calculate_description__isnull=False).exclude(calculate_description='')
        if self.product:
            queryset = queryset.filter(
                analytical_method__in=AnalyticalMethodProduct.objects.filter(
                    product=self.product).values_list('analytical_method_id', flat=True))
        self.fields['analytical_method_calculate'].queryset = queryset
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductCalculateRelationForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['analytical_method_calculate', 'factor', 'position']
        widgets = {
            'analytical_method_calculate': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
            'factor': TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        """Guarda la relación de cálculo asignándole el producto y el consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductVolumenStdRelationForm(ModelForm):
    """Formulario para registrar el volumen estándar en una relación de cálculo."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de volumen estándar."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductVolumenStdRelationForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['volumen_std', 'position']
        widgets = {
            'volumen_std': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
        }

    def save(self, commit=True):
        """Guarda el volumen estándar en la relación de cálculo asignando el consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductFactorRelationForm(ModelForm):
    """Formulario para registrar un factor constante en una relación de cálculo."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de factor constante."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductFactorRelationForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['factor', 'position']
        widgets = {
            'factor': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
        }

    def save(self, commit=True):
        """Guarda el factor constante en la relación de cálculo asignando el consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductSampleGramRelationForm(ModelForm):
    """Formulario para registrar la cantidad de muestra en una relación de cálculo."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de cantidad de muestra."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductSampleGramRelationForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['sample_quantity', 'position']
        widgets = {
            'sample_quantity': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
        }

    def save(self, commit=True):
        """Guarda la cantidad de muestra en la relación de cálculo asignando el consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductCalculateRelationAddForm(ModelForm):
    """Formulario para relacionar un cálculo registrado en un consecutivo anterior."""

    calculate_relation_related = ModelChoiceField(
        queryset=AnalyticalMethodCalculateRelation.objects.none(),
        label='Cálculo Relacionado Add',
        widget=Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
    )

    @staticmethod
    def _label_relation_add(obj):
        """Retorna la etiqueta del select: consecutivo, descripción y unidad de medida."""
        label = obj.calculate_description_relation
        if obj.unit_measure_calculate:
            label += f' ({obj.unit_measure_calculate})'
        if obj.consecutive_calcule:
            label = f'{obj.consecutive_calcule.consecutive} - {label}'
        return label

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los cálculos de consecutivos anteriores del producto."""
        self.product = kwargs.pop('product', None)
        self.dependent_calculation = kwargs.pop('dependent_calculation', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.product is None:
                self.product = self.instance.product
            if self.dependent_calculation is None:
                self.dependent_calculation = self.instance.consecutive_calcule
        queryset = AnalyticalMethodCalculateRelation.objects.filter(
            calculate_description_relation__isnull=False).exclude(calculate_description_relation='')
        if self.product:
            queryset = queryset.filter(product=self.product)
        if self.dependent_calculation:
            queryset = queryset.filter(
                consecutive_calcule__consecutive__lt=self.dependent_calculation.consecutive)
        field = self.fields['calculate_relation_related']
        field.queryset = queryset
        field.label_from_instance = self._label_relation_add
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        """Metadatos del formulario ProductCalculateRelationAddForm."""
        model = AnalyticalMethodCalculateRelation
        fields = ['calculate_relation_related', 'position']
        widgets = {
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
        }

    def save(self, commit=True):
        """Guarda la relación con el cálculo anterior asignando producto y consecutivo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                if self.dependent_calculation:
                    instance.consecutive_calcule = self.dependent_calculation
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProductCalculateRelationOperationForm(ProductCalculateRelationForm):
    """Formulario para cálculos relacionados con operaciones (+, −, ×, ÷) y agrupaciones.

    Extiende ProductCalculateRelationForm agregando la operación con la que el
    término se combina con el anterior dentro de su grupo, y la referencia al
    término padre para construir sub-expresiones con paréntesis.
    """

    parent = ModelChoiceField(
        queryset=AnalyticalMethodCalculateRelation.objects.none(),
        required=False,
        label='Agrupado Dentro de',
        widget=Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
    )

    @staticmethod
    def _label_parent(obj):
        """Retorna una etiqueta legible del término candidato a ser padre."""
        if obj.analytical_method_calculate:
            label = str(obj.analytical_method_calculate.calculate_description)
        elif obj.calculate_relation_related:
            label = str(obj.calculate_relation_related.calculate_description_relation)
        elif obj.volumen_std:
            label = f'Vol. STD: {obj.volumen_std}'
        elif obj.factor is not None:
            label = f'Constante: {obj.factor}'
        elif obj.sample_quantity:
            label = f'Muestra: {obj.sample_quantity}'
        else:
            label = 'Grupo'
        if obj.position:
            label += f' ({obj.position})'
        return label

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los posibles padres del mismo cálculo."""
        super().__init__(*args, **kwargs)
        parent_qs = AnalyticalMethodCalculateRelation.objects.filter(
            calculate_description_relation__in=[None, ''])
        if self.product:
            parent_qs = parent_qs.filter(product=self.product)
        if self.dependent_calculation:
            parent_qs = parent_qs.filter(consecutive_calcule=self.dependent_calculation)
        if self.instance and self.instance.pk:
            parent_qs = parent_qs.exclude(pk=self.instance.pk)
        field = self.fields['parent']
        field.queryset = parent_qs
        field.label_from_instance = self._label_parent

        col_classes = {
            # 'analytical_method_calculate': 'col-md-12',
            # 'operation': 'col-md-6',
            # 'position': 'col-md-6',
            # 'parent': 'col-md-12',
            'analytical_method_calculate': 'col-md-4',
            'subtract_blank': 'col-md-2',
            'factor': 'col-md-2',
            'standard_base': 'col-md-4',
            'operation': 'col-md-4',
            'position': 'col-md-3',
            'parent': 'col-md-3',
            'sample_quantity': 'col-md-2',
        }
        for field_name, form_field in self.fields.items():
            form_field.col_class = col_classes.get(field_name, 'col-md-6')

    class Meta(ProductCalculateRelationForm.Meta):
        """Metadatos del formulario ProductCalculateRelationOperationForm."""
        fields = ['analytical_method_calculate', 'operation', 'position', 'factor', 'parent']
        widgets = {
            **ProductCalculateRelationForm.Meta.widgets,
            'operation': Select(attrs={'class': 'form-control'}, choices=[('', 'Multiplicar (×)')] + OPERATION[1:]),
        }

    def clean_operation(self):
        """Normaliza la operación vacía a None (equivale a multiplicar)."""
        return self.cleaned_data.get('operation') or None

    def clean(self):
        """Valida que el término no se agrupe dentro de sí mismo ni de sus descendientes."""
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        if parent and self.instance and self.instance.pk:
            ancestor = parent
            while ancestor is not None:
                if ancestor.pk == self.instance.pk:
                    raise ValidationError({
                        'parent': 'Un término no puede agruparse dentro de sí mismo ni de sus descendientes.'
                    })
                ancestor = ancestor.parent
        return cleaned_data
