from django.forms import ModelForm, TextInput, Select

from core.product.models import SamplePoint, Stage, Product


# Creación de Productos
class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['process'].queryset = Process.objects.select_related('site').filter(site_id=self.site.id)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Product
        fields = ['code_product', 'description_product', 'process']
        widgets = {
            'code_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'description_product': TextInput(attrs={'class': 'form-control', 'required': True}),
            'process': Select(attrs={'class': 'form-control', 'required': True}),
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


# Creación de Etapas
class StageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.prod = kwargs.pop('prod')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Stage
        fields = ['stage_code', 'stage_name']
        widgets = {
            'stage_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'stage_name': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.product_id = self.prod.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de Etapas
class StageUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.stage = kwargs.pop('stage')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Stage
        fields = ['stage_code', 'stage_name']
        widgets = {
            'stage_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'stage_name': TextInput(attrs={'class': 'form-control', 'required': True})
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


# Creación de Puntos de Muestreo
class SamplePointForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        super().__init__(*args, **kwargs)
        # self.fields['stage'].queryset = Stage.objects.select_related('process').filter(process__site_id=self.site.id)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'stage', 'sample_frequency']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': TextInput(attrs={'class': 'form-control', 'required': True}),
            'stage': Select(attrs={'class': 'form-control', 'required': True}),
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


# Edición de Puntos de Muestreo
class SamplePointUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.sample = kwargs.pop('sample')
        super().__init__(*args, **kwargs)
        # self.fields['stage'].queryset = Stage.objects.select_related('product').filter(
        #     process__site_id=self.sample.stage.process.site.id)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplePoint
        fields = ['sample_point_code', 'sample_point_name', 'stage', 'sample_frequency']
        widgets = {
            'sample_point_code': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_point_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'sample_frequency': TextInput(attrs={'class': 'form-control', 'required': True}),
            'stage': Select(attrs={'class': 'form-control', 'required': True}),
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
