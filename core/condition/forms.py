from crum import get_current_user
from django.forms import ModelForm, TextInput, CheckboxInput, Select, Textarea, ValidationError
from django.utils import timezone

from core.condition.models import Condition, ConditionRegister


class ConditionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
            if form.name == 'enabled':
                form.field.widget.attrs['class'] = 'form-check-input'
            elif form.name == 'laboratory':
                form.field.widget.attrs['class'] = 'form-control select2'
                form.field.widget.attrs['style'] = 'width: 100%'
            else:
                form.field.widget.attrs['class'] = 'form-control'
        
        col_classes = {
            'laboratory': 'col-md-12',
            'area': 'col-md-6',
            'variable': 'col-md-6',
            'upper_limit': 'col-md-4',
            'lower_limit': 'col-md-4',
            'enabled': 'col-md-4'
        }
        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = Condition
        fields = ['laboratory', 'area', 'variable', 'upper_limit', 'lower_limit', 'enabled']
        widgets = {
            'laboratory': Select(),
            'area': TextInput(attrs={'placeholder': 'Ingrese el área'}),
            'variable': TextInput(attrs={'placeholder': 'Ingrese la variable'}),
            'upper_limit': TextInput(attrs={'placeholder': 'Límite superior'}),
            'lower_limit': TextInput(attrs={'placeholder': 'Límite inferior'}),
            'enabled': CheckboxInput()
        }


class ConditionRegisterForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condition2'] = self.fields['condition'].__class__(
            queryset=Condition.objects.filter(enabled=True),
            required=False,
            label='Área 2',
            widget=Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'})
        )
        self.fields['registered_data2'] = self.fields['registered_data'].__class__(
            required=False,
            label='Dato Registrado 2',
            widget=TextInput(attrs={'step': 'any', 'placeholder': 'Lectura', 'class': 'form-control'})
        )

        for field_name, field in self.fields.items():
            field.widget.attrs['autocomplete'] = 'off'
            if 'condition' in field_name:
                field.widget.attrs['class'] = 'form-control select2'
                field.widget.attrs['style'] = 'width: 100%'
            else:
                field.widget.attrs['class'] = 'form-control'

        col_classes = {
            'registered_data': 'col-md-2',
            'condition': 'col-md-4',
            'registered_data2': 'col-md-2',
            'condition2': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = ConditionRegister
        fields = ['condition', 'registered_data']
        widgets = {
            'registered_data': TextInput(attrs={'step': 'any', 'placeholder': 'Lectura', 'required':True}),
            'condition': Select(attrs={'class': 'form-control', 'style': 'width: 100%', 'required':True})
        }

    def clean(self):
        cleaned_data = super().clean()
        condition = cleaned_data.get('condition')
        registered_data = cleaned_data.get('registered_data')
        condition2 = cleaned_data.get('condition2')
        registered_data2 = cleaned_data.get('registered_data2')

        # Validación primer registro (obligatoriedad)
        if not condition or registered_data is None:
            raise ValidationError("El primer registro (Condición y Dato) es obligatorio.")

        # Validación segundo registro (si se inicia uno, se debe completar ambos campos)
        if condition2 or registered_data2:
            if not (condition2 and registered_data2 is not None):
                raise ValidationError("Si ingresa datos para el segundo registro, debe completar tanto la condición como el dato.")
            
            if condition == condition2:
                raise ValidationError("Las condiciones seleccionadas deben ser diferentes.")
            
            if condition and condition2 and condition.area != condition2.area:
                raise ValidationError("Las condiciones seleccionadas deben pertenecer al mismo área.")
        
        return cleaned_data

    def save(self, commit=True):
        user = get_current_user()
        registration_date = timezone.now()
        
        # Guardar primer registro
        instance1 = super().save(commit=False)
        instance1.registered_by_id = user.id
        instance1.registration_date = registration_date
        if commit:
            instance1.save()
        
        # Guardar segundo registro si existe
        condition2 = self.cleaned_data.get('condition2')
        registered_data2 = self.cleaned_data.get('registered_data2')
        
        if condition2 and registered_data2:
            instance2 = ConditionRegister(
                condition=condition2,
                registered_data=registered_data2,
                registered_by_id=user.id,
                registration_date=registration_date
            )
            if commit:
                instance2.save()
            return instance1, instance2
            
        return instance1


class ConditionRegisterActionsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
            form.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = ConditionRegister
        fields = ['actions']
        widgets = {
            'actions': Textarea(attrs={'placeholder': 'Ingrese las acciones o correcciones tomadas', 'rows': 3, 'cols': 3}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        user = get_current_user()
        try:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.actions_registered_by_id = user.id
                if commit:
                    instance.save()
                return instance
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data