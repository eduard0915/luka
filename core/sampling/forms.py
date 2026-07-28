"""Formularios para la aplicación de muestreo del laboratorio."""

from django.db.models import Q
from django.forms import ModelForm, TextInput, Select, TimeInput, DateTimeInput, FloatField
from django.core.exceptions import ValidationError
from django.utils import timezone
from crum import get_current_user
from openpyxl.compat import product

from core.sampling.models import SamplingGroup, SamplingProcess, SamplingAnalysisProcessing, \
    SamplingAnalysisProcessingRelation, SamplingAnalysis, MillimoleReacted
from core.product.models import SamplePoint, AnalyticalMethodProduct
from core.sampling.services import DAILY_PERIODICITY
from core.solution.models import SolutionStd
from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation, AnalyticalMethod

TYPE_SAMPLING = [('En Proceso', 'En Proceso'), ('Producto Terminado', 'Producto Terminado')]

SELECT = [(True, 'Si'), (False, 'No')]


class SamplingAnalysisProcessingForm(ModelForm):
    """Formulario para el registro de procesamiento de análisis volumétrico."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el análisis y configura los campos según el método."""
        self.analysis = kwargs.pop('analysis')
        super().__init__(*args, **kwargs)

        user = get_current_user()

        calcs = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(analytical_method_id=self.analysis.analytical_method.id)
        calc_con_label = calcs.exclude(sample_quantity__in=[None, '', False]).first()

        std_bases = self.analysis.analytical_method.analyticalmethodsolutionstd_set.values_list('solution_std_id', flat=True)
        self.fields['standard_solution'].queryset = SolutionStd.objects.select_related('solute_std').filter(
            solution_std_base_id__in=std_bases, preparation_confirmed=True, quantity_solution_std__gt=0, laboratory=user.laboratory)

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
        """Guarda el procesamiento volumétrico calculando la concentración de la muestra."""
        user = get_current_user()
        analytical_method_id = self.analysis.analytical_method.id
        var_num = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Denominador')

        try:
            instance = super().save(commit=False)
            instance.sample_analysis_id = self.analysis.id
            instance.analyzed_by_id = user.id
            instance.analyzed_date = timezone.now()
            instance.relational_calculation = False

            # Nota: Esto asume que solo hay un conjunto de cálculos (Num/Den) por método base
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


class SamplingAnalysisProcessingGravimetryForm(ModelForm):
    """Formulario para el registro de procesamiento de análisis gravimétrico."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el análisis y configura la etiqueta de cantidad de muestra."""
        self.analysis = kwargs.pop('analysis')
        super().__init__(*args, **kwargs)

        calcs = AnalyticalMethodCalculate.objects.select_related('analytical_method').filter(
            analytical_method_id=self.analysis.analytical_method.id)

        filter_sample = calcs.exclude(Q(sample_quantity__isnull=True) | Q(sample_quantity='')).first()

        self.fields['quantity_sample'].label = str(filter_sample.sample_quantity)

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'standard_solution': 'col-md-2',
            'quantity_standard': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessing
        fields = ['weight_obtained', 'quantity_sample']
        widgets = {
            'weight_obtained': TextInput(attrs={'class': 'form-control', 'required': True}),
            'quantity_sample': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        """Guarda el procesamiento gravimétrico calculando la concentración de la muestra."""
        user = get_current_user()
        analytical_method_id = self.analysis.analytical_method.id
        var_num = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Numerador')
        var_den = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id, position='Denominador')

        try:
            instance = super().save(commit=False)
            instance.sample_analysis_id = self.analysis.id
            instance.analyzed_by_id = user.id
            instance.analyzed_date = timezone.now()
            instance.relational_calculation = False

            base_calc = AnalyticalMethodCalculate.objects.filter(analytical_method_id=analytical_method_id).first()
            if base_calc:
                instance.analytical_method_calculate = base_calc

            if instance.weight_obtained is None or instance.quantity_sample is None:
                raise ValidationError(
                    "Los campos Peso Obtenido y cantidad de muestra son obligatorios")

            qty_wt = float(instance.weight_obtained)
            qty_sample = float(instance.quantity_sample)
            cifras_sign = instance.sample_analysis.analytical_method.sig_figs_result

            if qty_sample > 0:

                factor_num = 1
                variable_num = 1
                sample_num = 1

                for num in var_num:
                    if num.factor is not None:
                        factor_num *= float(num.factor)

                    if num.variable is not None:
                        variable_num *= float(qty_wt)

                    if num.sample_quantity and num.sample_quantity.strip():
                        sample_num = float(qty_sample)

                numerator = factor_num * sample_num * variable_num

                factor_den = 1
                variable_den = 1
                sample_den = 1

                for den in var_den:

                    if den.factor is not None:
                        factor_den *= float(den.factor)

                    if den.variable is not None:
                        variable_den *= float(qty_wt)

                    if den.sample_quantity and den.sample_quantity.strip():
                        sample_den = float(qty_sample)

                denominator = factor_den * sample_den * variable_den

                instance.concentration_sample = round((numerator / denominator), cifras_sign)
            else:
                instance.concentration_sample = 0

            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise ValidationError({'error': str(e)})


class SamplingAnalysisProcessingDirectForm(ModelForm):
    """Formulario para el registro de análisis por lectura directa (pH, densidad, viscosidad)."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el análisis y configura la etiqueta de concentración."""
        self.analysis = kwargs.pop('analysis', None)
        super().__init__(*args, **kwargs)
        self.fields['concentration_sample'].label = 'Registrar Lectura'
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'concentration_sample': 'col-md-4',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessing
        fields = ['concentration_sample']
        widgets = {
            'concentration_sample': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        """Guarda el procesamiento de lectura directa con la concentración registrada."""
        instance = super().save(commit=False)
        instance.sample_analysis_id = self.analysis.id
        instance.analyzed_by_id = get_current_user().id
        instance.analyzed_date = timezone.now()
        if commit:
            instance.save()
        return instance


class SamplingAnalysisProcessingRelationForm(ModelForm):
    """Formulario para el cálculo de parámetros con variables relacionadas."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el análisis, muestreo y relación de cálculo."""
        self.analysis = kwargs.pop('analysis', None)
        self.sampling = kwargs.pop('sampling', None)
        self.relation= kwargs.pop('relation', None)

        super().__init__(*args, **kwargs)
        self.fields['numerator'].widget.attrs['hidden'] = True
        self.fields['numerator'].label = ''
        self.fields['denominator'].widget.attrs['hidden'] = True
        self.fields['denominator'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'standard_solution': 'col-md-7',
            'quantity_standard': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessingRelation
        fields = ['numerator', 'denominator']
        widgets = {
            'numerator': TextInput(attrs={'class': 'form-control', 'required': True}),
            'denominator': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        """Guarda el cálculo relacional validando el denominador y calculando el resultado."""
        instance = super().save(commit=False)
        if self.relation is None:
            raise ValidationError('No se encontró una relación de cálculo asociada.')
        if not instance.denominator:
            raise ValidationError('El denominador no puede ser cero.')
        instance.calcule = round(instance.numerator / instance.denominator, self.relation.sig_figs)
        instance.sampling_analysis_id = self.analysis.id
        instance.sampling_process_id = self.sampling.id
        instance.analytical_method_calculate_relation_id = self.relation.id
        if commit:
            instance.save()
        return instance


class SamplingAnalysisForm(ModelForm):
    """Formulario para asociar un método analítico a una muestra."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario filtrando los métodos analíticos según el producto."""
        self.sampling_process = kwargs.pop('sampling_process')
        super().__init__(*args, **kwargs)

        if self.sampling_process.point_sampling:
            product_id = self.sampling_process.point_sampling.product.id
        else:
            product_id = self.sampling_process.group_sampling.sampling_point.product.id

        self.fields['analytical_method'].queryset = AnalyticalMethod.objects.filter(
            analyticalmethodproduct__product_id=product_id,
            enable_analytical_method=True
        ).distinct()

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
            field.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingAnalysis
        fields = ['analytical_method']
        widgets = {'analytical_method': Select(attrs={'class': 'form-control'})}

    def save(self, commit=True):
        """Guarda el análisis con el proceso de muestreo asociado."""
        instance = super().save(commit=False)
        instance.sampling_process = self.sampling_process
        if commit:
            instance.save()
        return instance

    def clean(self):
        """Valida que el método analítico no esté ya asociado a la muestra."""
        cleaned_data = super().clean()
        analytical_method = cleaned_data.get('analytical_method')

        if analytical_method and self.sampling_process:
            exists = SamplingAnalysis.objects.filter(
                sampling_process=self.sampling_process,
                analytical_method=analytical_method
            ).exists()

            if exists:
                self.add_error(
                    '',f'El método analítico "{analytical_method}" ya está asociado a esta muestra.')

        return cleaned_data


class SamplingGroupForm(ModelForm):
    """Formulario para la creación y edición de grupos de muestreo."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario excluyendo puntos de muestreo ya asignados a otros grupos."""
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        queryset = SamplePoint.objects.filter(
            enable_point=True, sample_frequency__isnull=False, periodicity__in=DAILY_PERIODICITY)

        if product:
            queryset = queryset.filter(product=product)

        # IDs de sampling_point ya usados en otros SamplingGroup existentes
        used_points = SamplingGroup.objects.exclude(
            pk=self.instance.pk
        ).exclude(
            sampling_point__isnull=True
        ).values_list('sampling_point_id', flat=True)

        queryset = queryset.exclude(pk__in=used_points)

        if self.instance.sampling_point_id:
            queryset = queryset | SamplePoint.objects.filter(pk=self.instance.sampling_point_id)

        self.fields['sampling_point'].queryset = queryset.distinct()

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
        """Guarda el grupo de muestreo y retorna los datos o errores."""
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


class SamplingGroupFullForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = SamplePoint.objects.filter(
            enable_point=True, sample_frequency__isnull=False, periodicity__in=DAILY_PERIODICITY)
        if self.instance.sampling_point_id:
            queryset = queryset | SamplePoint.objects.filter(pk=self.instance.sampling_point_id)
        self.fields['sampling_point'].queryset = queryset.distinct()
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
    """Formulario para la creación y edición de procesos de muestreo."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario configurando los campos de punto y grupo de muestreo."""
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
        """Valida que se seleccione grupo o punto de muestreo, y que sean excluyentes."""
        cleaned_data = super().clean()
        group_sampling = cleaned_data.get('group_sampling')
        point_sampling = cleaned_data.get('point_sampling')
        if not group_sampling and not point_sampling:
            raise ValidationError('Debe seleccionar un Grupo de Muestreo o un Punto de Muestreo.')
        if group_sampling:
            cleaned_data['point_sampling'] = None
        elif point_sampling:
            cleaned_data['group_sampling'] = None
        return cleaned_data

    def save(self, commit=True):
        """Guarda el proceso de muestreo asignando el usuario creador."""
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
    """Formulario para la actualización de la imagen de la muestra."""
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con autocompletado desactivado."""
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['image_sample']
        widgets = {'image_sample': TextInput(attrs={'class': 'form-control', 'type': 'file'})}

    def save(self, commit=True):
        """Guarda la imagen de la muestra y retorna los datos o errores."""
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
    """Formulario para la confirmación de recepción de muestra."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con autocompletado desactivado."""
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['image_sample']
        widgets = {'image_sample': TextInput(attrs={'class': 'form-control', 'type': 'file'})}

    def save(self, commit=True):
        """Confirma la muestra cambiando el estado a 'Confirmada' y asignando el usuario."""
        """Confirma la muestra cambiando el estado a 'Confirmada' y asignando el usuario."""
        form = super()
        try:
            if not form.is_valid():
                return {'error': form.errors}
            instance = form.save(commit=False)
            instance.sampling_confirmed_by_id = get_current_user().id
            instance.date_sampling = timezone.now()
            instance.status_sampling = 'Confirmada'
            instance.save()
            return instance
        except Exception as e:
            return {'error': str(e)}


class SamplingProcessInProcessForm(ModelForm):
    """Formulario para cambiar el estado de la muestra a 'En Proceso'."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario ocultando el campo de estado."""
        super().__init__(*args, **kwargs)
        self.fields['status_sampling'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['status_sampling']
        widgets = {'status_sampling': TextInput(attrs={'class': 'form-control', 'hidden': 'true'})}

    def save(self, commit=True):
        """Cambia el estado de la muestra a 'En Proceso'."""
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


class MillimoleReactedForm(ModelForm):
    """Formulario para el cálculo de milimoles en valoración por retroceso."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con el análisis y configura las soluciones estándar."""
        self.analysis = kwargs.pop('analysis')
        super().__init__(*args, **kwargs)

        user = get_current_user()

        std_bases = self.analysis.analytical_method.analyticalmethodsolutionstd_set.values_list('solution_std_id', flat=True)
        solutions_qs = SolutionStd.objects.select_related('solute_std').filter(
            solution_std_base_id__in=std_bases, preparation_confirmed=True,
            quantity_solution_std__gt=0, laboratory=user.laboratory,
        )

        self.fields['standard_solution_add'].queryset = solutions_qs
        self.fields['standard_solution_spend'].queryset = solutions_qs

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'standard_solution_add': 'col-md-9',
            'standard_solution_spend': 'col-md-9',
            'milliliter_std_add': 'col-md-3',
            'milliliter_std_spend': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = MillimoleReacted
        fields = ['standard_solution_add', 'milliliter_std_add', 'standard_solution_spend', 'milliliter_std_spend', 'quantity_sample']
        widgets = {
            'standard_solution_add': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'milliliter_std_add': TextInput(attrs={'class': 'form-control', 'required': True}),
            'standard_solution_spend': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'milliliter_std_spend': TextInput(attrs={'class': 'form-control', 'required': True}),
            'quantity_sample': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        """Guarda el registro calculando los milimoles que reaccionaron: (V1*C1) - (V2*C2)."""
        try:
            instance = super().save(commit=False)
            instance.sampling_analysis_id = self.analysis.id

            v1 = float(instance.milliliter_std_add)
            c1 = float(instance.standard_solution_add.concentration_std)
            v2 = float(instance.milliliter_std_spend)
            c2 = float(instance.standard_solution_spend.concentration_std)

            instance.millimole = round((v1 * c1) - (v2 * c2), 6)

            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise ValidationError({'error': str(e)})


class SamplingProcessApprovedForm(ModelForm):
    """Formulario para la aprobación de control de calidad de muestra."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario ocultando la etiqueta de aprobación."""
        super().__init__(*args, **kwargs)
        self.fields['approved'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingProcess
        fields = ['approved']
        widgets = {'approved': Select(attrs={'class': 'form-control'}, choices=SELECT)}

    def save(self, commit=True):
        """Aprueba la muestra cambiando el estado a 'Aprobado' y asignando el usuario."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.approved_by_id = get_current_user().id
                data.date_approved = timezone.now()()
                data.status_sampling = 'Aprobado'
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
