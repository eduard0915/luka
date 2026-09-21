"""Formularios para la aplicación de muestreo del laboratorio."""

from django.db.models import Q
from django.forms import ModelForm, Form, TextInput, Select, TimeInput, DateTimeInput, FloatField, FileField, FileInput, HiddenInput
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
from core.analytical_method.services import build_gravimetry_data, evaluate_gravimetry_terms
from core.utils import round_sig_figs

TYPE_SAMPLING = [('En Proceso', 'En Proceso'), ('Producto Terminado', 'Producto Terminado')]

SELECT = [(True, 'Si'), (False, 'No')]


def _marks_net_weight(calc):
    """Indica si una fila de cálculo marca el peso neto (variable, peso bruto o peso filtro)."""
    return any(
        (getattr(calc, field) or '').strip()
        for field in ('variable', 'gross_weight', 'weight_of_filter')
    )


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

        # La alícuota solo se solicita cuando la ecuación del método la incluye.
        if calcs.filter(aliquot=True).exists():
            self.fields['aliquot'].required = True
            self.fields['aliquot'].label = 'Alícuota'
        else:
            self.fields['aliquot'].required = False
            self.fields['aliquot'].widget = HiddenInput()

        self.fields['quantity_standard'].required = True

        # El segundo volumen estándar solo se solicita cuando el método tiene dos volúmenes estándar.
        if calcs.exclude(volumen_std__isnull=True).exclude(volumen_std='').count() >= 2:
            self.fields['quantity_standard_two'].required = True
            self.fields['quantity_standard'].label = 'mL STD Totales'
            self.fields['quantity_standard_two'].label = 'mL STD 2'
        else:
            self.fields['quantity_standard_two'].required = False
            self.fields['quantity_standard_two'].widget = HiddenInput()

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'standard_solution': 'col-md-6',
            'quantity_standard': 'col-md-3',
            'quantity_standard_two': 'col-md-3',
            'aliquot': 'col-md-3',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessing
        fields = ['standard_solution', 'quantity_standard', 'quantity_standard_two', 'quantity_sample', 'aliquot']
        widgets = {
            'standard_solution': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'quantity_standard': TextInput(attrs={'class': 'form-control', 'required': True}),
            'quantity_standard_two': TextInput(attrs={'class': 'form-control'}),
            'quantity_sample': TextInput(attrs={'class': 'form-control', 'required': True}),
            'aliquot': TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        """Guarda el procesamiento volumétrico calculando la concentración de la muestra."""
        user = get_current_user()
        analytical_method_id = self.analysis.analytical_method.id
        var_num = AnalyticalMethodCalculate.objects.filter(
            analytical_method_id=analytical_method_id, position='Numerador').order_by('date_creation')
        var_den = AnalyticalMethodCalculate.objects.filter(
            analytical_method_id=analytical_method_id, position='Denominador').order_by('date_creation')

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
            if instance.standard_solution.average_concentration:
                conc_std = float(instance.standard_solution.average_concentration)
            else:
                conc_std = float(instance.standard_solution.concentration_std)
            cifras_sign = instance.sample_analysis.analytical_method.sig_figs_result

            if qty_sample > 0:
                # Volúmenes estándar en orden de creación (primero = V_Total, segundo = V_2)
                volume_rows = sorted(
                    [c for c in list(var_num) + list(var_den)
                     if c.volumen_std and str(c.volumen_std).strip()],
                    key=lambda c: c.date_creation
                )
                second_volume_pks = {c.pk for c in volume_rows[1:]} if len(volume_rows) > 1 else set()

                def row_value(row):
                    """Valor de una fila de cálculo: producto de sus términos no vacíos."""
                    value = 1.0
                    has_part = False
                    if row.factor is not None:
                        value *= float(row.factor)
                        has_part = True
                    if row.sample_quantity and str(row.sample_quantity).strip():
                        value *= qty_sample
                        has_part = True
                    if row.volumen_std and str(row.volumen_std).strip():
                        if row.pk in second_volume_pks:
                            if instance.quantity_standard_two in (None, ''):
                                raise ValidationError('El campo mL Estándar 2 es obligatorio')
                            value *= float(instance.quantity_standard_two)
                        else:
                            value *= qty_std
                        has_part = True
                    if row.sln_std_base is not None:
                        value *= conc_std
                        has_part = True
                    if row.aliquot:
                        if instance.aliquot in (None, ''):
                            raise ValidationError('El campo alícuota es obligatorio')
                        value *= float(instance.aliquot)
                        has_part = True
                    return value if has_part else None

                def combine(rows):
                    """Combina los valores de las filas según su operación con el término anterior.

                    El segundo volumen estándar resta del primero por defecto (V_Total - V_2),
                    igual que la ecuación mostrada en el detalle del método; una operación
                    explícita en la fila tiene prioridad.
                    """
                    result = None
                    for row in rows:
                        value = row_value(row)
                        if value is None:
                            continue
                        if result is None:
                            result = value
                            continue
                        if row.operation:
                            operation = row.operation
                        elif row.pk in second_volume_pks:
                            operation = 'subtract'
                        else:
                            operation = 'multiply'
                        if operation == 'add':
                            result += value
                        elif operation == 'subtract':
                            result -= value
                        elif operation == 'divide':
                            result = result / value if value else 0
                        else:
                            result *= value
                    return 1.0 if result is None else result

                numerator = combine(var_num)
                denominator = combine(var_den)
                instance.concentration_sample = (
                    round_sig_figs(numerator / denominator, cifras_sign) if denominator else 0
                )
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
            'weight_obtained': 'col-md-4',
            'weight_of_filter': 'col-md-4',
            'quantity_sample': 'col-md-4'
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SamplingAnalysisProcessing
        fields = ['weight_obtained', 'weight_of_filter', 'quantity_sample']
        widgets = {
            'weight_obtained': TextInput(attrs={'class': 'form-control', 'required': True}),
            'weight_of_filter': TextInput(attrs={'class': 'form-control', 'required': True}),
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

            if instance.weight_obtained is None or instance.quantity_sample is None or instance.weight_of_filter is None:
                raise ValidationError(
                    "Los campos Peso Obtenido y cantidad de muestra son obligatorios")

            qty_wt = float(instance.weight_obtained)
            qty_filter = float(instance.weight_of_filter)
            qty_net = qty_wt - qty_filter
            qty_sample = float(instance.quantity_sample)
            cifras_sign = instance.sample_analysis.analytical_method.sig_figs_result

            if qty_sample > 0:

                factor_num = 1
                sample_num = 1
                # El peso neto (Peso Bruto - Peso Filtro) entra UNA sola vez por posición:
                # las filas de peso bruto y peso filtro conforman el mismo término
                net_weight_num = any(_marks_net_weight(num) for num in var_num)

                for num in var_num:
                    if num.factor is not None:
                        factor_num *= float(num.factor)

                    if num.sample_quantity and num.sample_quantity.strip():
                        sample_num = float(qty_sample)

                variable_num = float(qty_net) if net_weight_num else 1

                numerator = factor_num * sample_num * variable_num

                factor_den = 1
                sample_den = 1
                net_weight_den = any(_marks_net_weight(den) for den in var_den)

                for den in var_den:

                    if den.factor is not None:
                        factor_den *= float(den.factor)

                    if den.sample_quantity and den.sample_quantity.strip():
                        sample_den = float(qty_sample)

                variable_den = float(qty_net) if net_weight_den else 1

                denominator = factor_den * sample_den * variable_den

                raw_value = numerator / denominator if denominator else 0

                # La ecuación del método puede combinar el cálculo básico con
                # términos constantes (por ejemplo 100 - cálculo básico).
                calcules = AnalyticalMethodCalculate.objects.filter(
                    analytical_method_id=analytical_method_id)
                _, calc_terms = build_gravimetry_data(calcules)
                calc_constants = [term for term in calc_terms if term.term_type == 'constant']
                if calc_constants:
                    term_units = calc_terms
                else:
                    term_units = list(self.analysis.analytical_method.gravimetryterm_set.all())
                if term_units:
                    evaluated = evaluate_gravimetry_terms(raw_value, term_units)
                    if evaluated is not None:
                        raw_value = evaluated

                instance.concentration_sample = round_sig_figs(raw_value, cifras_sign)
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
        instance.calcule = round_sig_figs(instance.numerator / instance.denominator, self.relation.sig_figs)
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
            'first_hour_sampling': TimeInput(format='%H:%M', attrs={'class': 'form-control', 'data-timepicker': '1', 'placeholder': 'HH:MM', 'autocomplete': 'off'}),
            'number_sampling_day': TextInput(attrs={'class': 'form-control', 'readonly': True})
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
            'first_hour_sampling': TimeInput(format='%H:%M', attrs={'class': 'form-control', 'data-timepicker': '1', 'placeholder': 'HH:MM', 'autocomplete': 'off'}),
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
            self.fields['point_sampling'].queryset = SamplePoint.objects.filter(enable_point=True, sample_type='Producto Terminado')
            # self.fields['point_sampling'].queryset = SamplePoint.objects.filter(enable_point=True, sample_type='Producto Terminado', sample_frequency__isnull=True)
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


class MassiveSampleAnalysisUploadForm(Form):
    """Formulario para el cargue masivo de análisis de metales pesados desde Excel (.xlsx)."""

    file = FileField(
        label='Archivo Excel',
        widget=FileInput(attrs={'class': 'form-control', 'accept': '.xlsx', 'required': True})
    )

    def clean_file(self):
        """Valida que el archivo sea .xlsx y no supere los 10 MB."""
        excel_file = self.cleaned_data['file']
        if not excel_file.name.lower().endswith('.xlsx'):
            raise ValidationError('El archivo debe tener extensión .xlsx')
        if excel_file.size > 10 * 1024 * 1024:
            raise ValidationError('El archivo no debe superar los 10 MB.')
        return excel_file


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
