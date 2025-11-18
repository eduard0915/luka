from django import forms
from django.forms import ModelForm, TextInput, Select

from core.company.models import Site
from core.laboratory.models import Laboratory

BOOLEAN = [(True, 'Si'), (False, 'No')]


class LaboratoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['site'].queryset = Site.objects.filter(site_enable=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

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

    # def clean_laboratory_name(self):
    #     laboratory_name = self.cleaned_data.get('laboratory_name')
    #     if laboratory_name:
    #         laboratory_name = laboratory_name.strip()
    #         # Validar que no exista otro laboratorio con el mismo nombre
    #         qs = Laboratory.objects.filter(laboratory_name__iexact=laboratory_name)
    #         if self.instance.pk:
    #             qs = qs.exclude(pk=self.instance.pk)
    #         if qs.exists():
    #             raise forms.ValidationError('Ya existe un laboratorio con este nombre')
    #     return laboratory_name
