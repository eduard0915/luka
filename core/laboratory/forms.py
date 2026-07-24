"""Formularios de la aplicación de laboratorios.

Define el formulario para la creación y edición de laboratorios.
"""  # noqa: E501

from django import forms
from django.forms import ModelForm, TextInput, Select

from core.company.models import Site
from core.laboratory.models import Laboratory

BOOLEAN = [(True, 'Si'), (False, 'No')]


class LaboratoryForm(ModelForm):
    """Formulario para crear y editar un laboratorio."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando sedes activas y asignando clases CSS."""
        super().__init__(*args, **kwargs)
        self.fields['site'].queryset = Site.objects.filter(site_enable=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'laboratory_name': 'col-md-6',
            'enable_laboratory': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = Laboratory
        fields = ['laboratory_name', 'site', 'enable_laboratory']
        widgets = {
            'laboratory_name': TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Ingrese el nombre del laboratorio'
            }),
            'site': Select(attrs={'class': 'form-control', 'required': True}),
            'enable_laboratory': Select(attrs={
                'class': 'form-control',
                'required': True
            }, choices=BOOLEAN),
        }

    def save(self, commit=True):
        """Guarda el laboratorio y retorna los datos o un mensaje de error."""
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
