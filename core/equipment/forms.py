from django import forms
from django.forms import ModelForm, TextInput, Select, DateInput, FileInput, NumberInput
from core.equipment.models import EquipmentInstrumental
from core.laboratory.models import Laboratory
from core.user.views.user.views import User

BOOLEAN = [(True, 'Si'), (False, 'No')]


# Creación de Equipos Instrumentales
class EquipmentInstrumentalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['laboratory'].queryset = Laboratory.objects.filter(enable_laboratory=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = EquipmentInstrumental
        fields = [
            'code_equipment', 'description_equipment', 'supplier_equipment',
            'brand_equipment', 'model_equipment', 'serie_equipment',
            'laboratory', 'responsible_user', 'photo_equipment', 'manual_equipment'
        ]
        widgets = {
            'code_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'supplier_equipment': TextInput(attrs={'class': 'form-control','required': True}),
            'brand_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'model_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'serie_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'laboratory': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'photo_equipment': FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'manual_equipment': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'})
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
