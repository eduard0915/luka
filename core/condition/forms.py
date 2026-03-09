from crum import get_current_user
from django.forms import ModelForm, TextInput, CheckboxInput, DateTimeInput, Select, NumberInput, Textarea
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
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
            if form.name == 'condition':
                form.field.widget.attrs['class'] = 'form-control select2'
                form.field.widget.attrs['style'] = 'width: 100%'
            else:
                form.field.widget.attrs['class'] = 'form-control'

        col_classes = {
            'registered_data': 'col-md-2',
            'condition': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = ConditionRegister
        fields = ['condition', 'registered_data']
        widgets = {
            'registered_data': TextInput(attrs={'step': 'any', 'placeholder': 'Lectura'}),
            'condition': Select(attrs={'class': 'form-control', 'style': 'width: 100%'})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        user = get_current_user()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.registered_by_id = user.id
                data.registration_date = timezone.localtime()
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


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