"""Formularios de Django para la gestión de empresas, plantas y procesos en el LIMS."""

from django.forms import ModelForm, TextInput, FileInput

from core.company.models import *


class CompanyForm(ModelForm):
    """Formulario para la creación y edición de empresas.

    Permite gestionar los datos de configuración de la empresa, incluyendo
    nombre, NIT, dirección, ciudad, país, alerta de capacitaciones y logotipo.
    """

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de empresa ocultando la etiqueta del logotipo
        y desactivando el autocompletado en todos los campos visibles.
        """
        super().__init__(*args, **kwargs)
        self.fields['company_logo'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Company
        fields = [
            'company_name', 'company_nit', 'company_address', 'company_city', 'company_country', 'training_alert',
            'company_logo']
        widgets = {
            'company_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_nit': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_address': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_city': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_country': TextInput(attrs={'class': 'form-control', 'required': True}),
            'training_alert': TextInput(attrs={'class': 'form-control', 'required': True}),
            'company_logo': FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'company_logo': 'Logo de la empresa en jpg o png 256Kb Max.'
        }

    def save(self, commit=True):
        """Guarda los datos del formulario y retorna un diccionario con el resultado.

        Retorna un diccionario con los datos guardados si la validación es exitosa,
        o un diccionario con la clave 'error' en caso contrario.
        """
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


class SiteForm(ModelForm):
    """Formulario para la creación de plantas (sitios) asociadas a una empresa.

    Recibe el identificador de la empresa a la que pertenecerá la planta
    y lo asigna automáticamente al guardar.
    """

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario extrayendo la empresa del contexto y
        desactivando el autocompletado en todos los campos visibles.
        """
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
        """Guarda la planta asignándole la empresa proporcionada y retorna el resultado.

        Crea la instancia sin confirmar, asigna el ID de la empresa y luego
        persiste los datos en la base de datos.
        """
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


class SiteUpdateForm(ModelForm):
    """Formulario para la edición de plantas existentes.

    Permite modificar el nombre, dirección, ciudad y país de una planta.
    """

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de edición de planta desactivando el autocompletado."""
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
        """Guarda los cambios realizados a la planta y retorna el resultado en un diccionario."""
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
    """Formulario para la creación de procesos asociados a una planta.

    Recibe la planta a la que pertenecerá el proceso y asigna
    automáticamente la relación al guardar.
    """

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario extrayendo la planta del contexto y
        desactivando el autocompletado en los campos visibles.
        """
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
        """Guarda el proceso asignándole la planta proporcionada y retorna el resultado.

        Crea la instancia sin confirmar, asigna el ID de la planta y luego
        persiste los datos en la base de datos.
        """
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
    """Formulario para la edición de procesos existentes.

    Permite modificar el nombre de un proceso asociado a una planta.
    """

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario de edición de proceso desactivando el autocompletado."""
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
        """Guarda los cambios realizados al proceso y retorna el resultado en un diccionario."""
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
