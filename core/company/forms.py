from django.forms import ModelForm, TextInput, FileInput

from core.company.models import *


# Creación y edición de Empresa
class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_logo'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Company
        fields = ['company_name', 'company_nit', 'company_address', 'company_city', 'company_country', 'company_logo']
        widgets = {
            'company_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_nit': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_address': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_city': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_country': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_logo': FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'company_logo': 'Logo de la empresa en jpg o png 256Kb Max.'
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


# Creación de Plantas
class SiteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Site
        fields = ['site_name', 'site_address', 'site_city', 'site_country']
        widgets = {
            'site_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_address': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_city': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_country': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.company_id = self.company.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de Plantas
class SiteUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Site
        fields = ['site_name', 'site_address', 'site_city', 'site_country']
        widgets = {
            'site_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_address': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_city': TextInput(attrs={'class': 'form-control', 'required': True}),
            'site_country': TextInput(attrs={'class': 'form-control', 'required': True})
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


class ProcessForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Process
        fields = ['process_name']
        widgets = {
            'process_name': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.site_id = self.site.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ProcessUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Process
        fields = ['process_name']
        widgets = {
            'process_name': TextInput(attrs={'class': 'form-control', 'required': True}),
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
