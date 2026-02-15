from random import choices

from django.forms import ModelForm, TextInput, Select, NumberInput, Textarea

from core.analytical_method.models import AnalyticalMethod, AnalyticalMethodSolution, AnalyticalMethodSolutionStd, \
    AnalyticalMethodReagent, AnalyticalMethodEquipment, AnalyticalMethodMaterial, AnalyticalMethodProcedure, \
    AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation
from core.laboratory.models import Laboratory
from core.solution.models import SolutionStdBase, SolutionBase

BOOLEAN = [(True, 'Si'), (False, 'No')]

TYPE_METHOD = [
    ('Volumetrico', 'Volumétrico'),
    ('Volumetrico por Retroceso', 'Volumétrico por Retroceso'),
    ('Volumetrico - Mezcla', 'Volumétrico - Mezcla'),
    ('Gravimetrico', 'Gravimétrico'),
    ('Espectrofotometrico', 'Espectrofotométrico'),
    ('Espectroscopico', 'Espectroscópico'),
    ('Lectura Directa', 'Lectura Directa')
]

UNIT_CALCULATE = [
    ('%p/p', '%p/p'),
    ('%p/v', '%p/v'),
    ('mg/L', 'mg/L'),
    ('ppm', 'ppm')
]

POSITION = [('Numerador', 'Numerador'), ('Denominador', 'Denominador')]


# Creación de Métodos Analíticos
class AnalyticalMethodForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['laboratory'].queryset = Laboratory.objects.filter(enable_laboratory=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'description_analytical_method': 'col-md-5',
            'code_analytical_method': 'col-md-3',
            'enable_analytical_method': 'col-md-2',
            'sample_size': 'col-md-2',
            'type_method': 'col-md-4',
            'laboratory': 'col-md-4',
            'sig_figs_result': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = AnalyticalMethod
        fields = [
            'description_analytical_method',
            'code_analytical_method',
            'enable_analytical_method',
            'sample_size',
            'type_method',
            'laboratory',
            'sig_figs_result',
        ]
        widgets = {
            'description_analytical_method': TextInput(attrs={
                'class': 'form-control', 'required': True, 'placeholder': 'Nombre del método'}),
            'code_analytical_method': TextInput(attrs={
                'class': 'form-control', 'required': True, 'placeholder': 'Código del método'}),
            'enable_analytical_method': Select(attrs={'class': 'form-control', 'required': True}, choices=BOOLEAN),
            'sample_size': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'type_method': Select(attrs={'class': 'form-control', 'required': True}, choices=TYPE_METHOD),
            'laboratory': Select(attrs={'class': 'form-control', 'required': True}),
            'sig_figs_result': TextInput(attrs={'class': 'form-control', 'required': True, 'min': 0}),
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


class AnalyticalMethodSolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['solution'].queryset = SolutionBase.objects.filter(enable_solution=True)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodSolution
        fields = ['solution']
        widgets = {
            'solution': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodSolutionStdForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['solution_std'].queryset = SolutionStdBase.objects.filter(enable_solution_std=True)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodSolutionStd
        fields = ['solution_std']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodReagentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodReagent
        fields = ['reagent']
        widgets = {
            'reagent': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodEquipmentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodEquipment
        fields = ['equipment_instrumental']
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodMaterialForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodMaterial
        fields = ['material_instrumental']
        widgets = {
            'material_instrumental': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación de paso a paso o procedimiento
class AnalyticalMethodProcedureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodProcedure
        fields = ['procedure']
        widgets = {
            'procedure': Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese el procedimiento'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación de descripción de cálculo
class AnalyticalMethodCalculeDescriptionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['calculate_description', 'unit_measure_calculate']
        widgets = {
            'calculate_description': TextInput(attrs={'class': 'form-control'}),
            'unit_measure_calculate': Select(attrs={'class': 'form-control'}, choices=UNIT_CALCULATE),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación Volumen de Estándar
class AnalyticalMethodVolumenStdForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación Factor Denominador
class AnalyticalMethodFactorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Agregar Cantidad de Muestra
class AnalyticalMethodSampleGramForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['sample_quantity', 'position']
        widgets = {
            'sample_quantity': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Relación de Cálculos
class AnalyticalMethodCalculateRelationRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        if self.analytical_method:
            self.fields['analytical_method_calculate'].queryset = AnalyticalMethodCalculate.objects.filter(
                analytical_method__analyticalmethodproduct__product__analyticalmethodproduct__analytical_method=self.analytical_method
            ).exclude(calculate_description__isnull=True).exclude(
                calculate_description__exact='').distinct()
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['analytical_method_calculate', 'position']
        widgets = {
            'analytical_method_calculate': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Relación de Cálculos
class AnalyticalMethodCalculeRelationDescriptionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodVolumenStdRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodFactorRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodSampleGramRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analytical_method = kwargs.pop('analytical_method', None)
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
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
