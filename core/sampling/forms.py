from django.forms import ModelForm, TextInput, Select, TimeInput, DateTimeInput
from django.core.exceptions import ValidationError
from django.utils import timezone
from crum import get_current_user
from core.sampling.models import SamplingGroup, SamplingProcess, SamplingAnalysisProcessing, \
    SamplingAnalysisProcessingRelation
from core.product.models import SamplePoint
from core.solution.models import SolutionStd
from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation

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
        analytical_method_id = self.analysis.analytical_method.id
        var_num = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Denominador')

        try:
            instance = super().save(commit=False)
            instance.sample_analysis_id = self.analysis.id
            instance.analyzed_by_id = user.id
            instance.analyzed_date = timezone.localtime()
            instance.relational_calculation = False
            
            # Asociar el primer cálculo encontrado si existe
            # Nota: Esto asume que solo hay un conjunto de cálculos (Num/Den) por método base, 
            # o que todos pertenecen a la misma descripción lógica.
            base_calc = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id).first()
            if base_calc:
                instance.analytical_method_calculate = base_calc

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

                    if num.sample_quantity and num.sample_quantity.strip():
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

                    if den.sample_quantity and den.sample_quantity.strip():
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


class SamplingAnalysisProcessingRelationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.analysis = kwargs.pop('analysis')
        self.relation = kwargs.pop('relation')
        super().__init__(*args, **kwargs)

        # Determinar qué campos mostrar basados en position de AnalyticalMethodCalculateRelation
        all_relations = AnalyticalMethodCalculateRelation.objects.filter(
            analytical_method_id=self.analysis.analytical_method.id,
            calculate_description_relation=self.relation.calculate_description_relation
        )

        var_num = all_relations.filter(position__iexact='Numerador').exists()
        var_den = all_relations.filter(position__iexact='Denominador').exists()

        if not var_num:
            self.fields.pop('numerator', None)
        else:
            self.fields['numerator'].label = 'Numerador'

        if not var_den:
            self.fields.pop('denominator', None)
        else:
            self.fields['denominator'].label = 'Denominador'

        for field in self.visible_fields():
            field.field.widget.attrs['autocomplete'] = 'off'
            field.field.widget.attrs['class'] = 'form-control'
            if field.name in ['numerator', 'denominator']:
                field.field.widget.attrs['readonly'] = 'readonly'

    class Meta:
        model = SamplingAnalysisProcessingRelation
        fields = ['numerator', 'denominator']
        widgets = {
            'numerator': TextInput(attrs={'readonly': 'readonly'}),
            'denominator': TextInput(attrs={'readonly': 'readonly'}),
        }

    def save(self, commit=True):
        all_relations = AnalyticalMethodCalculateRelation.objects.select_related('analytical_method').filter(
            analytical_method_id=self.analysis.analytical_method.id,
            calculate_description_relation=self.relation.calculate_description_relation
        )
        var_num = all_relations.filter(position__iexact='Numerador')
        var_den = all_relations.filter(position__iexact='Denominador')

        try:
            # Obtener el procesamiento base (priorizando el análisis actual, luego el proceso en común)
            base_processing = SamplingAnalysisProcessing.objects.filter(
                sample_analysis_id=self.analysis.id,
                relational_calculation=False
            ).first()

            if not base_processing:
                base_processing = SamplingAnalysisProcessing.objects.filter(
                    sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                    relational_calculation=False
                ).order_by('-analyzed_date').first()

            if not base_processing:
                raise ValidationError("No existe un procesamiento base registrado para esta muestra (SamplingProcess).")

            instance = super().save(commit=False)
            instance.sampling_analysis_id = self.analysis.id
            instance.analytical_method_calculate_relation = self.relation

            qty_std = float(base_processing.quantity_standard)
            qty_sample = float(base_processing.quantity_sample)
            cifras_sign = instance.sampling_analysis.analytical_method.sig_figs_result

            if qty_sample > 0:
                factor_num = 1
                sample_num = 1
                std_num = 1
                relation_num = 1
                used_prev_num = False

                for num in var_num:
                    if num.factor is not None:
                        factor_num *= float(num.factor)
                    if num.sample_quantity and num.sample_quantity.strip():
                        sample_num = float(qty_sample)
                    if num.volumen_std is not None:
                        std_num = qty_std
                    if num.analytical_method_calculate is not None:
                        prev_processing = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                            analytical_method_calculate=num.analytical_method_calculate,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()
                        if prev_processing:
                            relation_num *= prev_processing.concentration_sample
                            used_prev_num = True
                        else:
                            raise ValidationError(f"No se encontró el resultado previo para: {num.analytical_method_calculate.calculate_description} en esta muestra")

                # Búsqueda por posición si no se encontró por cálculo específico
                if not used_prev_num:
                    prev_processing_num = SamplingAnalysisProcessing.objects.filter(
                        sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                        analytical_method_calculate__position__iexact='Numerador',
                        relational_calculation=False
                    ).order_by('-analyzed_date').first()
                    if prev_processing_num:
                        relation_num = prev_processing_num.concentration_sample
                        used_prev_num = True

                # Fallback final: si no se definió un cálculo relacionado explícito, usar el procesamiento base actual o el último de la muestra
                if not used_prev_num:
                    if base_processing:
                        relation_num = base_processing.concentration_sample
                    else:
                        base_prev = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()
                        if base_prev:
                            relation_num = base_prev.concentration_sample

                numerator = std_num * factor_num * sample_num * relation_num
                instance.numerator = numerator
                
                factor_den = 1
                sample_den = 1
                std_den = 1
                relation_den = 1
                used_prev_den = False

                for den in var_den:
                    if den.factor is not None:
                        factor_den *= float(den.factor)
                    if den.sample_quantity and den.sample_quantity.strip():
                        sample_den = float(qty_sample)
                    if den.volumen_std is not None:
                        std_den = qty_std
                    if den.analytical_method_calculate is not None:
                        prev_processing = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                            analytical_method_calculate=den.analytical_method_calculate,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()
                        if prev_processing:
                            relation_den *= prev_processing.concentration_sample
                            used_prev_den = True
                        else:
                            raise ValidationError(f"No se encontró el resultado previo para: {den.analytical_method_calculate.calculate_description} en esta muestra")

                # Búsqueda por posición si no se encontró por cálculo específico
                if not used_prev_den:
                    prev_processing_den = SamplingAnalysisProcessing.objects.filter(
                        sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                        analytical_method_calculate__position__iexact='Denominador',
                        relational_calculation=False
                    ).order_by('-analyzed_date').first()
                    if prev_processing_den:
                        relation_den = prev_processing_den.concentration_sample
                        used_prev_den = True

                # Fallback final: si no se definió un cálculo relacionado explícito, usar el procesamiento base actual o el último de la muestra
                if not used_prev_den:
                    if base_processing:
                        relation_den = base_processing.concentration_sample
                    else:
                        base_prev_den = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=self.analysis.sampling_process_id,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()
                        if base_prev_den:
                            relation_den = base_prev_den.concentration_sample

                denominator = std_den * factor_den * sample_den * relation_den
                instance.denominator = denominator

                instance.calcule = round((numerator / denominator), cifras_sign)
            else:
                instance.calcule = 0

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
