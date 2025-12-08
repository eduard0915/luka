from django.forms import ModelForm, TextInput, Select, NumberInput

from core.analytical_method.models import AnalyticalMethod
from core.laboratory.models import Laboratory

BOOLEAN = [(True, 'Si'), (False, 'No')]

TYPE_METHOD = [('Volumetrico', 'Volumétrico'), ('Gravimetrico', 'Gravimétrico'), ('Espectrofotometrico', 'Espectrofotométrico'), ('Espectroscopico', 'Espectroscópico')]


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
