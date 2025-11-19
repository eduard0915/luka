from django import forms
from django.forms import ModelForm, TextInput, Select, DateInput, FileInput, NumberInput
from core.equipment.models import EquipmentInstrumental
from core.laboratory.models import Laboratory
from django.contrib.auth.models import User

BOOLEAN = [(True, 'Si'), (False, 'No')]


# Creación de Equipos Instrumentales
class EquipmentInstrumentalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['laboratory'].queryset = Laboratory.objects.filter(enable_laboratory=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True).order_by('first_name',
                                                                                                'last_name')

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = EquipmentInstrumental
        fields = [
            'code_equipment', 'description_equipment', 'supplier_equipment',
            'brand_equipment', 'model_equipment', 'serie_equipment',
            'laboratory', 'date_start_use', 'date_disabled', 'time_use',
            'responsible_user', 'photo_equipment', 'manual_equipment', 'enable_equipment'
        ]
        widgets = {
            'code_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Código del equipo'
            }),
            'description_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Descripción del equipo'
            }),
            'supplier_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Proveedor del equipo'
            }),
            'brand_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Marca'
            }),
            'model_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Modelo'
            }),
            'serie_equipment': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Número de serie'
            }),
            'laboratory': Select(attrs={
                'class': 'form-control select2',
                'required': True,
                'style': 'width: 100%'
            }),
            'date_start_use': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_disabled': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time_use': NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Horas de uso'
            }),
            'responsible_user': Select(attrs={
                'class': 'form-control select2',
                'required': True,
                'style': 'width: 100%'
            }),
            'photo_equipment': FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'manual_equipment': FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'enable_equipment': Select(attrs={
                'class': 'form-control',
                'required': True
            }, choices=BOOLEAN),
        }

    def clean_code_equipment(self):
        code_equipment = self.cleaned_data.get('code_equipment')
        if code_equipment:
            code_equipment = code_equipment.strip().upper()
            # Validar que no exista otro equipo con el mismo código
            qs = EquipmentInstrumental.objects.filter(code_equipment__iexact=code_equipment)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un equipo con este código')
        return code_equipment

    def clean_serie_equipment(self):
        serie_equipment = self.cleaned_data.get('serie_equipment')
        if serie_equipment:
            serie_equipment = serie_equipment.strip().upper()
            # Validar que no exista otro equipo con el mismo número de serie
            qs = EquipmentInstrumental.objects.filter(serie_equipment__iexact=serie_equipment)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un equipo con este número de serie')
        return serie_equipment

    def clean_time_use(self):
        time_use = self.cleaned_data.get('time_use')
        if time_use is not None and time_use < 0:
            raise forms.ValidationError('El tiempo de uso no puede ser negativo')
        return time_use

    def clean(self):
        cleaned_data = super().clean()
        date_start_use = cleaned_data.get('date_start_use')
        date_disabled = cleaned_data.get('date_disabled')

        # Validar que la fecha de inactivación sea posterior a la fecha de inicio
        if date_start_use and date_disabled:
            if date_disabled < date_start_use:
                self.add_error('date_disabled',
                               'La fecha de inactivación debe ser posterior a la fecha de inicio de uso')

        return cleaned_data
