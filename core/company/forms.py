from django.forms import ModelForm, TextInput, FileInput

from core.company.models import Company


class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            'company_logo': FileInput(attrs={'class': 'form-control', 'required': True}),
        }
        help_texts = {
            'company_logo': 'jpg o png 256Kb Max.'
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
