from django.forms import ModelForm, TextInput, Select, TimeInput, DateTimeInput
from django.core.exceptions import ValidationError
from django.utils import timezone
from crum import get_current_user
from core.sampling.models import SamplingGroup, SamplingProcess, SamplingAnalysisProcessing
from core.product.models import SamplePoint
from core.solution.models import SolutionStd
from core.analytical_method.models import AnalyticalMethodCalculate

TYPE_SAMPLING = [('En Proceso', 'En Proceso'), ('Producto Terminado', 'Producto Terminado')]

class SamplingAnalysisProcessingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analysis = kwargs.pop('analysis')
        super().__init__(*args, **kwargs)
        calcs = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(analytical_method_id=self.analysis.analytical_method.id)
        calc_con_label = calcs.exclude(sample_quantity__in=[None, '', False]).first()

        std_bases = self.analysis.analytical_method.analyticalmethodsolutionstd_set.values_list('solution_std_id', flat=True)
        self.fields['standard_solution'].queryset = SolutionStd.objects.select_related('solute_std').filter(
            solution_std_base_id__in=std_bases,
            preparation_confirmed=True,
            quantity_solution_std__gt=0)
        
        if calc_con_label and calc_con_label.sample_quantity:
            self.fields['quantity_sample'].label = str(calc_con_label.sample_quantity)

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'standard_solution': 'col-md-7',
            'quantity_standard': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessing
        fields = ['standard_solution', 'quantity_standard', 'quantity_sample']
        widgets = {
            'standard_solution': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'quantity_standard': TextInput(attrs={'class': 'form-control', 'required': True}),
            'quantity_sample': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        user = get_current_user()
        var_num = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(analytical_method_id=self.analysis.analytical_method.id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(analytical_method_id=self.analysis.analytical_method.id, position='Denominador')

        try:
            instance = super().save(commit=False)
            instance.sample_analysis_id = self.analysis.id
            instance.analyzed_by_id = user.id
            instance.analyzed_date = timezone.localtime()

            if instance.quantity_standard is None or instance.quantity_sample is None or instance.standard_solution.concentration_std is None:
                raise ValidationError(
                    "Los campos cantidad estándar, cantidad de muestra y concentración del estándar son obligatorios")

            qty_std = float(instance.quantity_standard)
            qty_sample = float(instance.quantity_sample)
            cifras_sign = instance.sample_analysis.analytical_method.sig_figs_result

            if qty_sample > 0:

                factor_num = 1
                sample_num = 1
                std_num = 1

                for num in var_num:
                    if num.factor is not None:
                        factor_num *= float(num.factor)

                    if num.sample_quantity is not None:
                        sample_num = float(qty_sample)

                    if num.volumen_std is not None:
                        std_num = qty_std

                numerator = std_num * factor_num * sample_num

                factor_den = 1
                sample_den = 1
                std_den = 1

                for den in var_den:

                    if den.factor is not None:
                        factor_den *= float(den.factor)

                    if den.sample_quantity is not None:
                        sample_den = float(qty_sample)

                    if den.volumen_std is not None:
                        std_den = qty_std

                denominator = std_den * factor_den * sample_den

                instance.concentration_sample = round((numerator / denominator), cifras_sign)
            else:
                instance.concentration_sample = 0

            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise ValidationError({'error': str(e)})

class SamplingGroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sampling_point'].queryset = SamplePoint.objects.filter(enable_point=True, sample_frequency__isnull=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        col_classes = {'sampling_point': 'col-md-6'}
        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingGroup
        fields = ['sampling_point', 'first_hour_sampling', 'number_sampling_day']
        widgets = {
            'sampling_point': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'first_hour_sampling': TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'number_sampling_day': TextInput(attrs={'class': 'form-control', 'required': True})
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

class SamplingProcessForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            self.fields['point_sampling'].queryset = SamplePoint.objects.filter(enable_point=True, sample_type='Producto Terminado', sample_frequency__isnull=True)
            form.field.widget.attrs['autocomplete'] = 'off'
        col_classes = {'point_sampling': 'col-md-4', 'group_sampling': 'col-md-4', 'batch_number': 'col-md-2'}
        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingProcess
        fields = ['type_sampling', 'group_sampling', 'point_sampling', 'date_sampling_scheduled', 'batch_number']
        widgets = {
            'group_sampling': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'point_sampling': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'type_sampling': Select(attrs={'class': 'form-control', 'style': 'width: 100%'}, choices=TYPE_SAMPLING),
            'date_sampling_scheduled': DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'data-datetime': '1', 'placeholder': 'yyyy-mm-dd HH:MM'}),
            'batch_number': TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        group_sampling = cleaned_data.get('group_sampling')
        point_sampling = cleaned_data.get('point_sampling')
        if group_sampling:
            cleaned_data['point_sampling'] = None
        if point_sampling:
            cleaned_data['group_sampling'] = None
        return cleaned_data

    def save(self, commit=True):
        data = {}
        user = get_current_user()
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.sampling_created_by_id = user.id
                data.automatic_sampling = False
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class SamplingProcessImageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['image_sample']
        widgets = {'image_sample': TextInput(attrs={'class': 'form-control', 'type': 'file'})}

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

class SamplingProcessConfirmedForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['image_sample']
        widgets = {'image_sample': TextInput(attrs={'class': 'form-control', 'type': 'file'})}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.sampling_confirmed_by_id = get_current_user().id
                data.date_sampling = timezone.localtime()
                data.status_sampling = 'Confirmada'
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class SamplingProcessInProcessForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_sampling'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['status_sampling']
        widgets = {'status_sampling': TextInput(attrs={'class': 'form-control', 'hidden': 'true'})}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.status_sampling = 'En Proceso'
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
