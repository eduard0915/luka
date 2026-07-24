"""Formularios de la aplicación de equipos para la gestión de equipos
instrumentales, material instrumental, mantenimientos, calibraciones,
verificaciones y patrones de referencia."""

from datetime import date

import dateutil.utils
from crum import get_current_user
from dateutil.relativedelta import relativedelta
from django import forms
from django.forms import ModelForm, TextInput, Select, DateInput, FileInput, NumberInput, Textarea
from django.utils import timezone

from core.equipment.models import EquipmentInstrumental, MaterialInstrumental, Maintenance, Calibration, Verification, DailyVerification, ReferencePattern
from core.laboratory.models import Laboratory
from core.user.views.user.views import User

BOOLEAN = [(True, 'Si'), (False, 'No')]

PARAMETER = [
    ('Temperatura', 'Temperatura'), ('Humedad', 'Humedad'), ('Masa', 'Masa'), ('Presión', 'Presión'), ('pH', 'pH'), ('No aplica', 'No aplica')
]

UNIT_TOLERANCE = [('No aplica', 'No aplica'), ('Kg', 'Kg'), ('g', 'g'), ('mg', 'mg'), ('mL', 'mL'), ('%v/v', '%v/v'), ('nm', 'nm')]

TYPE_MAINTENANCE = [('Preventivo', 'Preventivo'), ('Correctivo', 'Correctivo')]


class VerificationForm(ModelForm):
    """Formulario para el registro y edición de verificaciones intermedias de equipos instrumentales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de verificación configurando los queryset de equipos habilitados y usuarios activos."""
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'date_verification': 'col-md-2',
            'equipment_instrumental': 'col-md-5',
            'comply': 'col-md-2',
            'parameter_verified': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = Verification
        fields = [
            'equipment_instrumental', 'date_verification', 'verified_by', 'comply', 'parameter_verified',
            'responsible_user', 'observation_verification', 'reference_pattern',
            'report_verification'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'date_verification': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
            'verified_by': TextInput(attrs={'class': 'form-control', 'required': True}),
            'parameter_verified': Select(attrs={'class': 'form-control', 'required': True}, choices=PARAMETER),
            'observation_verification': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'comply': Select(choices=BOOLEAN, attrs={'class': 'form-control', 'required': True}),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'report_verification': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
            'reference_pattern': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }

    def save(self, commit=True):
        """Guarda el registro de verificación calculando la fecha de la próxima verificación."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.date_verification_next = data.date_verification + relativedelta(months=data.equipment_instrumental.intermediate_verification)
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class MaintenanceForm(ModelForm):
    """Formulario para el registro y edición de mantenimientos de equipos instrumentales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de mantenimiento configurando el queryset de equipos habilitados."""
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'date_maintenance': 'col-md-2',
            'equipment_instrumental': 'col-md-5',
            'description_maintenance': 'col-md-4',
            'parts_change_maintenance': 'col-md-4',
            'file_maintenance': 'col-md-4',
            'type_maintenance': 'col-md-2',
            'parameter': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = Maintenance
        fields = [
            'equipment_instrumental', 'date_maintenance', 'type_maintenance', 'maintenance_by',
            'description_maintenance', 'parts_change_maintenance', 'file_maintenance'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'date_maintenance': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
            'type_maintenance': Select(attrs={'class': 'form-control', 'required': True}, choices=TYPE_MAINTENANCE),
            'maintenance_by': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_maintenance': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'rows': 3}),
            'parts_change_maintenance': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'rows': 3}),
            'file_maintenance': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }

    def save(self, commit=True):
        """Guarda el registro de mantenimiento calculando la fecha del próximo mantenimiento."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.next_date_maintenance = data.date_maintenance + relativedelta(
                    months=data.equipment_instrumental.frequency_maintenance)
                data.responsible_user_id = get_current_user().id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class CalibrationForm(ModelForm):
    """Formulario para el registro y edición de calibraciones de equipos instrumentales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de calibración configurando el queryset de equipos habilitados."""
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
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
            'equipment_instrumental', 'date_calibration', 'calibrated_by', 'comply', 'parameter',
            'observation_calibration', 'certificate_calibration'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'date_calibration': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
            'calibrated_by': TextInput(attrs={'class': 'form-control', 'required': True}),
            'parameter': Select(attrs={'class': 'form-control', 'required': True}, choices=PARAMETER),
            'observation_calibration': Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'comply': Select(choices=BOOLEAN, attrs={'class': 'form-control', 'required': True}),
            'certificate_calibration': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
        }

    def save(self, commit=True):
        """Guarda el registro de calibración calculando la fecha de la próxima calibración."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                years= relativedelta(date.today(), data.equipment_instrumental.date_calibration_fix).years
                year_calibration = (data.equipment_instrumental.frequency_calibration / 12)
                data.date_calibration_next = data.equipment_instrumental.date_calibration_fix + relativedelta(years=1 if years == 0 else years) + relativedelta(years=year_calibration)
                data.responsible_user_id = get_current_user().id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class DailyVerificationForm(ModelForm):
    """Formulario para el registro y edición de verificaciones diarias de equipos instrumentales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de verificación diaria configurando el queryset de equipos habilitados."""
        super().__init__(*args, **kwargs)
        self.fields['equipment_instrumental'].queryset = EquipmentInstrumental.objects.filter(enable_equipment=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'verification_result_daily': 'col-md-2',
            'equipment_instrumental': 'col-md-5',
            'observation_verification': 'col-md-5',
            'reference_pattern': 'col-md-2',
            'parameter_verified': 'col-md-2'
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = DailyVerification
        fields = [
            'equipment_instrumental', 'parameter_verified', 'reference_pattern', 'verification_result_daily',
            'observation_verification'
        ]
        widgets = {
            'equipment_instrumental': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'parameter_verified': Select(attrs={'class': 'form-control', 'required': True}, choices=UNIT_TOLERANCE),
            'reference_pattern': Select(attrs={'class': 'form-control', 'required': True}),
            'verification_result_daily': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'observation_verification': Textarea(attrs={'class': 'form-control', 'rows': 1})
        }

    def save(self, commit=True):
        """Guarda el registro de verificación diaria calculando el error y determinando si cumple con la tolerancia."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.date_verification_daily = timezone.now()
                data.verified_by_id = get_current_user().id
                data.error = round((data.reference_pattern.magnitude_pattern - data.verification_result_daily) * 1000, 4)
                tolerance = data.equipment_instrumental.tolerance
                if data.error > -tolerance or data.error < tolerance:
                    data.comply = True
                else:
                    data.comply = False
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class EquipmentInstrumentalForm(ModelForm):
    """Formulario para el registro y edición de equipos instrumentales."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de equipo instrumental configurando los queryset de laboratorios habilitados y usuarios activos."""
        super().__init__(*args, **kwargs)
        self.fields['laboratory'].queryset = Laboratory.objects.filter(enable_laboratory=True)
        self.fields['responsible_user'].queryset = User.objects.filter(is_active=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = EquipmentInstrumental
        fields = [
            'code_equipment', 'description_equipment', 'supplier_equipment',
            'brand_equipment', 'model_equipment', 'serie_equipment', 'frequency_calibration',
            'intermediate_verification', 'unit_tolerance', 'tolerance',
            'laboratory', 'responsible_user', 'photo_equipment', 'manual_equipment', 'date_calibration_fix'
        ]
        widgets = {
            'code_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'supplier_equipment': TextInput(attrs={'class': 'form-control','required': True}),
            'brand_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'model_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'serie_equipment': TextInput(attrs={'class': 'form-control', 'required': True}),
            'frequency_calibration': TextInput(attrs={'class': 'form-control'}),
            'intermediate_verification': TextInput(attrs={'class': 'form-control'}),
            'tolerance': TextInput(attrs={'class': 'form-control'}),
            'laboratory': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'unit_tolerance': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=UNIT_TOLERANCE),
            'responsible_user': Select(attrs={'class': 'form-control', 'required': True, 'style': 'width: 100%'}),
            'photo_equipment': FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'manual_equipment': FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'date_calibration_fix': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'required': True, 'data-datepicker': '1', 'autocomplete': 'off'}),
        }

    def clean_code_equipment(self):
        """Valida que el código del equipo no exista previamente en la base de datos."""
        code_equipment = self.cleaned_data.get('code_equipment')
        if code_equipment:
            code_equipment = code_equipment.strip().upper()
            qs = EquipmentInstrumental.objects.filter(code_equipment__iexact=code_equipment)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un equipo con este código')
        return code_equipment

    def clean_serie_equipment(self):
        """Valida que el número de serie del equipo no exista previamente en la base de datos."""
        serie_equipment = self.cleaned_data.get('serie_equipment')
        if serie_equipment:
            serie_equipment = serie_equipment.strip().upper()
            qs = EquipmentInstrumental.objects.filter(serie_equipment__iexact=serie_equipment)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un equipo con este número de serie')
        return serie_equipment


class MaterialInstrumentalForm(ModelForm):
    """Formulario para el registro y edición de materiales instrumentales o de laboratorio."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de material instrumental configurando el queryset de usuarios activos."""
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
        """Valida que el código del material no exista previamente en la base de datos."""
        code_instrumental = self.cleaned_data.get('code_instrumental')
        if code_instrumental:
            code_instrumental = code_instrumental.strip().upper()
            qs = MaterialInstrumental.objects.filter(code_instrumental__iexact=code_instrumental)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un material con este código')
        return code_instrumental


class ReferencePatternForm(ModelForm):
    """Formulario para el registro de patrones de referencia asociados a un equipo instrumental."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de patrón de referencia extrayendo el equipo instrumental del contexto."""
        self.equipment_instrumental = kwargs.pop('equipment_instrumental', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'description_pattern': 'col-md-6',
            'magnitude_pattern': 'col-md-3',
            'unit_pattern': 'col-md-3',
            'date_expire_calibration': 'col-md-5',
            'certificate_calibration': 'col-md-7'
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = ReferencePattern
        fields = ['description_pattern', 'magnitude_pattern', 'unit_pattern', 'date_expire_calibration', 'certificate_calibration']
        widgets = {
            'description_pattern': TextInput(attrs={'class': 'form-control'}),
            'magnitude_pattern': NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'unit_pattern': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}, choices=UNIT_TOLERANCE),
            'date_expire_calibration': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'data-datepicker': '1', 'autocomplete': 'off'}),
            'certificate_calibration': FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def save(self, commit=True):
        """Guarda el registro del patrón de referencia asociándolo al equipo instrumental correspondiente."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.equipment_instrumental_id = self.equipment_instrumental.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ReferencePatternUpdateForm(ModelForm):
    """Formulario para la edición de patrones de referencia."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de edición de patrón de referencia."""
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'description_pattern': 'col-md-6',
            'magnitude_pattern': 'col-md-3',
            'unit_pattern': 'col-md-3',
            'date_expire_calibration': 'col-md-5',
            'certificate_calibration': 'col-md-7'
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = ReferencePattern
        fields = ['description_pattern', 'magnitude_pattern', 'unit_pattern', 'date_expire_calibration', 'certificate_calibration']
        widgets = {
            'description_pattern': TextInput(attrs={'class': 'form-control'}),
            'magnitude_pattern': NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'unit_pattern': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}, choices=UNIT_TOLERANCE),
            'date_expire_calibration': DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'data-datepicker': '1', 'autocomplete': 'off'}),
            'certificate_calibration': FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def save(self, commit=True):
        """Guarda los cambios realizados al patrón de referencia."""
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
