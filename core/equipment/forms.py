from dateutil.relativedelta import relativedelta
from django import forms
from django.forms import ModelForm, TextInput, Select, DateInput, FileInput, NumberInput
from core.equipment.models import EquipmentInstrumental, MaterialInstrumental, Maintenance, Calibration
from core.laboratory.models import Laboratory
from core.user.views.user.views import User

BOOLEAN = [(True, 'Si'), (False, 'No')]


PARAMETER = [('temperature', 'Temperatura'), ('humidity', 'Humedad'), ('mass', 'Masa'), ('pressure', 'Presión'), ('No aplica', 'No aplica')]


# Mantenimiento
class MaintenanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Maintenance
        fields = [
            'equipment_instrumental', 'date_maintenance', 'type_maintenance',
            'maintenance_by', 'description_maintenance', 'parts_change_maintenance',
            'responsible_user', 'file_maintenance'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'date_maintenance': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
            'type_maintenance': TextInput(attrs={'class': 'form-control', 'required': True}),
            'maintenance_by': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_maintenance': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'rows': 3}),
            'parts_change_maintenance': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'rows': 3}),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'file_maintenance': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }


# Calibración
class CalibrationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'date_calibration': 'col-md-2',
            'equipment_instrumental': 'col-md-5',
            'comply': 'col-md-2',
            'parameter': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = Calibration
        fields = [
            'equipment_instrumental', 'date_calibration',
            'calibrated_by', 'comply', 'parameter', 'responsible_user', 'observation_calibration',
            'certificate_calibration'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'date_calibration': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
            'calibrated_by': TextInput(attrs={'class': 'form-control', 'required': True}),
            'parameter': Select(attrs={'class': 'form-control', 'required': True}, choices=PARAMETER),
            'observation_calibration': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'comply': Select(choices=BOOLEAN, attrs={'class': 'form-control', 'required': True}),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'certificate_calibration': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.date_calibration_next = data.date_calibration + relativedelta(months=data.equipment_instrumental.frequency_calibration)
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data



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


# Material Instrumental o de Laboratorio
class MaterialInstrumentalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = MaterialInstrumental
        fields = [
            'code_instrumental', 'description_instrumental', 'supplier_equipment',
            'brand_instrumental', 'responsible_user', 'photo_instrumental'
        ]
        widgets = {
            'code_instrumental': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_instrumental': TextInput(attrs={'class': 'form-control', 'required': True}),
            'supplier_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'brand_instrumental': TextInput(attrs={'class': 'form-control', 'required': True}),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'photo_instrumental': FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_code_instrumental(self):
        code_instrumental = self.cleaned_data.get('code_instrumental')
        if code_instrumental:
            code_instrumental = code_instrumental.strip().upper()
            # Validar que no exista otro material con el mismo código
            qs = MaterialInstrumental.objects.filter(code_instrumental__iexact=code_instrumental)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un material con este código')
        return code_instrumental
