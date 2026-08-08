"""Formularios para la aplicación de métodos analíticos.

Define los formularios para la creación y edición de métodos analíticos,
incluyendo soluciones, reactivos, equipos, materiales, procedimientos y cálculos.
"""

from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelChoiceField, TextInput, Select, Textarea, CheckboxInput

from core.analytical_method.models import *
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
    ('', '----'),
    ('%p/p', '%p/p'),
    ('%p/v', '%p/v'),
    ('g/mL', 'g/mL'),
    ('mg/L', 'mg/L'),
    ('ppm', 'ppm'),
    ('ppb', 'ppb'),
    ('mg/Kg', 'mg/Kg')
]

POSITION = [('Numerador', 'Numerador'), ('Denominador', 'Denominador')]

STEP = [('', '')] + [(i, i) for i in range(1, 20)]


# Creación de Métodos Analíticos
class AnalyticalMethodForm(ModelForm):
    """Formulario para la creación y edición de métodos analíticos."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando laboratorios habilitados y configurando clases CSS."""
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
        """Guarda el método analítico y retorna los datos o errores."""
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
    """Formulario para asociar una solución a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando soluciones base habilitadas."""
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
        """Guarda la relación solución-método analítico."""
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
    """Formulario para asociar una solución estándar a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando soluciones estándar base habilitadas."""
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
        """Guarda la relación solución estándar-método analítico."""
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
    """Formulario para asociar un reactivo a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con los reactivos disponibles."""
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
        """Guarda la relación reactivo-método analítico."""
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
    """Formulario para asociar un equipo a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con los equipos disponibles."""
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
        """Guarda la relación equipo-método analítico."""
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
    """Formulario para asociar un material a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con los materiales disponibles."""
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
        """Guarda la relación material-método analítico."""
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
    """Formulario para agregar un paso de procedimiento a un método analítico."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el paso numerado automáticamente."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        if self.analytical_method and not self.instance.pk:
            last_step = AnalyticalMethodProcedure.objects.filter(
                analytical_method=self.analytical_method
            ).order_by('-step_procedure').first()
            if last_step:
                self.fields['step_procedure'].initial = last_step.step_procedure + 1
            else:
                self.fields['step_procedure'].initial = 1
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodProcedure
        fields = ['step_procedure', 'procedure']
        widgets = {
            'procedure': Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese el procedimiento'}),
            'step_procedure': Select(attrs={'class': 'form-control'}, choices=STEP),
        }

    def save(self, commit=True):
        """Guarda el paso del procedimiento."""
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
    """Formulario para la descripción del cálculo de concentración."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de descripción de cálculo."""
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
        """Guarda la descripción del cálculo."""
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
    """Formulario para el volumen estándar en el cálculo."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de volumen estándar."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)

        std_ids = AnalyticalMethodSolutionStd.objects.filter(
            analytical_method=self.analytical_method).values_list('solution_std', flat=True)

        self.fields['sln_std_base'].queryset = SolutionStdBase.objects.filter(pk__in=std_ids)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['sln_std_base', 'position', 'subtract_blank']
        widgets = {
            'sln_std_base': Select(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
            'subtract_blank': Select(attrs={'class': 'form-control'}, choices=BOOLEAN)
        }

    def save(self, commit=True):
        """Guarda el volumen estándar del cálculo."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                self.volumen_std = 'mL Gastados'
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Activar o Desactivar Resta de Blanco
class AnalyticalMethodSubtractBlankForm(ModelForm):
    """Formulario para activar o desactivar la resta de blanco en el cálculo."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de resta de blanco."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['subtract_blank'].label = 'Restar Blanco'
        self.fields['subtract_blank'].help_text = 'Al activarse, la ecuación resta el Blanco al Volumen Estándar.'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['subtract_blank']
        widgets = {
            'subtract_blank': CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        """Guarda el estado de la resta de blanco del cálculo."""
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
    """Formulario para el factor constante en el cálculo."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de factor constante."""
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
        """Guarda el factor constante del cálculo."""
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
    """Formulario para la variable de muestra en el cálculo."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de variable de muestra."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['sample_quantity'].required = True
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['sample_quantity', 'position']
        widgets = {
            'sample_quantity': TextInput(attrs={'class': 'form-control', 'required': True}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
        }

    def save(self, commit=True):
        """Guarda la variable de muestra del cálculo."""
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
class AnalyticalMethodCalculateRelationForm(ModelForm):
    """Formulario para crear un cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de cálculo relacionado."""
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
        """Guarda el cálculo relacionado."""
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
    """Formulario para la descripción de un cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de descripción de cálculo relacionado."""
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
        """Guarda la descripción del cálculo relacionado."""
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
    """Formulario para el volumen estándar en cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de volumen estándar relacionado."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)

        std_ids = AnalyticalMethodSolutionStd.objects.filter(
            analytical_method=self.analytical_method).values_list('solution_std', flat=True)

        self.fields['standard_base'].queryset = SolutionStdBase.objects.filter(pk__in=std_ids)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['standard_base', 'position', 'subtract_blank']
        widgets = {
            'standard_base': Select(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
            'subtract_blank': Select(attrs={'class': 'form-control'}, choices=BOOLEAN)
        }

    def save(self, commit=True):
        """Guarda el volumen estándar del cálculo relacionado."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                instance.volumen_std = 'mL Gastados'
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class AnalyticalMethodFactorRelationForm(ModelForm):
    """Formulario para el factor constante en cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de factor relacionado."""
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
        """Guarda el factor del cálculo relacionado."""
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
    """Formulario para la variable de muestra en cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de muestra relacionada."""
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
        """Guarda la variable de muestra del cálculo relacionado."""
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


# Agregar Variable Relacional
class AnalyticalMethodVariableRelationForm(ModelForm):
    """Formulario para la variable adicional en cálculo relacionado."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de variable relacionada."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['variable'].required = True
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculateRelation
        fields = ['variable', 'position']
        widgets = {
            'variable': TextInput(attrs={'class': 'form-control'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION),
        }

    def save(self, commit=True):
        """Guarda la variable del cálculo relacionado."""
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


# Cálculo Relacionado con Operación
class AnalyticalMethodCalculateRelationOperationForm(AnalyticalMethodCalculateRelationForm):
    """Formulario para cálculos relacionados del método con operaciones (+, −, ×, ÷) y agrupaciones.

    Extiende AnalyticalMethodCalculateRelationForm agregando la operación con la que el
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
    def _is_group(obj):
        """Indica si el término es un nodo contenedor (grupo) sin contenido propio."""
        return not (obj.analytical_method_calculate or obj.volumen_std or obj.standard_base
                    or obj.factor is not None or obj.variable or obj.sample_quantity)

    @staticmethod
    def _label_parent(obj):
        """Retorna una etiqueta legible del término candidato a ser padre."""
        if obj.analytical_method_calculate:
            label = str(obj.analytical_method_calculate.calculate_description)
        elif obj.volumen_std:
            label = f'Vol. STD: {obj.volumen_std}'
        elif obj.factor is not None:
            label = f'Constante: {obj.factor}'
        elif obj.standard_base:
            label = f'Sol. STD: {obj.standard_base}'
        elif obj.variable:
            label = f'Variable: {obj.variable}'
        elif obj.sample_quantity:
            label = f'Muestra: {obj.sample_quantity}'
        else:
            label = 'Grupo'
        if obj.position:
            label += f' ({obj.position})'
        return label

    def _build_group_consecutive(self, parent_qs):
        """Construye un mapeo pk -> consecutivo para los grupos según orden de creación."""
        groups = [cr.pk for cr in parent_qs.order_by('date_creation') if self._is_group(cr)]
        return {pk: idx + 1 for idx, pk in enumerate(groups)}

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los posibles padres del mismo método."""
        super().__init__(*args, **kwargs)

        std_ids = AnalyticalMethodSolutionStd.objects.filter(
            analytical_method=self.analytical_method).values_list('solution_std', flat=True)
        self.fields['standard_base'].queryset = SolutionStdBase.objects.filter(pk__in=std_ids)

        parent_qs = AnalyticalMethodCalculateRelation.objects.filter(
            calculate_description_relation__in=[None, ''])
        if self.analytical_method:
            parent_qs = parent_qs.filter(analytical_method=self.analytical_method)
        if self.instance and self.instance.pk:
            parent_qs = parent_qs.exclude(pk=self.instance.pk)
        field = self.fields['parent']
        field.queryset = parent_qs
        group_consec = self._build_group_consecutive(parent_qs)

        def _label_for(obj):
            if obj.pk in group_consec:
                label = f'Grupo (sub-expresión) -{group_consec[obj.pk]}'
                if obj.position:
                    label += f' ({obj.position})'
                return label
            return self._label_parent(obj)

        field.label_from_instance = _label_for

        col_classes = {
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

    class Meta(AnalyticalMethodCalculateRelationForm.Meta):
        """Metadatos del formulario AnalyticalMethodCalculateRelationOperationForm."""
        fields = [
            'analytical_method_calculate', 'standard_base', 'subtract_blank', 'factor', 'operation', 'position',
            'sample_quantity', 'parent'
        ]
        widgets = {
            **AnalyticalMethodCalculateRelationForm.Meta.widgets,
            'subtract_blank': Select(attrs={'class': 'form-control'}, choices=BOOLEAN),
            'factor': TextInput(attrs={'class': 'form-control'}),
            'sample_quantity': TextInput(attrs={'class': 'form-control'}),
            'standard_base': Select(attrs={'class': 'form-control'}),
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


# Agregar Variable a calculo
class AnalyticalMethodVariableForm(ModelForm):
    """Formulario para la variable adicional en el cálculo."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de variable adicional."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        self.fields['variable'].required = True
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = AnalyticalMethodCalculate
        fields = ['variable', 'position']
        widgets = {
            'variable': TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Descripción de la variable'}),
            'position': Select(attrs={'class': 'form-control'}, choices=POSITION)
        }

    def save(self, commit=True):
        """Guarda la variable adicional del cálculo."""
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


class SolutionStdBackValuationForm(ModelForm):
    """Formulario para la solución estándar de retrovaloración."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de retrovaloración."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStdBackValuation
        fields = ['solution_std', 'volume_std_back']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control', 'required': True}),
            'volume_std_back': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        """Guarda la configuración de retrovaloración."""
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


class SolutionStdBackValuationSpentForm(ModelForm):
    """Formulario para el gasto de solución estándar de retrovaloración."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de gasto de retrovaloración."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStdBackValuation
        fields = ['solution_std']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        """Guarda el gasto de retrovaloración."""
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.analytical_method:
                    instance.analytical_method = self.analytical_method
                self.volume_std_back = 0
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class HeavyMetalForm(ModelForm):
    """Formulario para la creación y edición de componentes de corridas (metales pesados)."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario asignando el método analítico de la instancia actual."""
        self.analytical_method = kwargs.pop('analytical_method', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = HeavyMetal
        fields = ['metal_description', 'unit_measure', 'detection_limit', 'quantification_limit']
        widgets = {
            'metal_description': TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Descripción del metal'}),
            'unit_measure': Select(attrs={'class': 'form-control', 'required': True}, choices=UNIT_CALCULATE),
            'detection_limit': TextInput(attrs={'class': 'form-control', 'step': 'any'}),
            'quantification_limit': TextInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def save(self, commit=True):
        """Guarda el componente de corrida asignando el método analítico."""
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


class DependentCalculationForm(ModelForm):
    """Formulario para crear/editar un cálculo dependiente con consecutivo autoasignado."""

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = DependentCalculation
        fields = ['calcule_description']
        widgets = {
            'calcule_description': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                instance = super().save(commit=False)
                if self.product:
                    instance.product = self.product
                    last = DependentCalculation.objects.filter(product=self.product).order_by('consecutive').last()
                    instance.consecutive = last.consecutive + 1 if last else 1
                instance.save()
                data = instance
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
