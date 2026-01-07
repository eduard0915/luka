from datetime import timedelta

from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput
from django.utils import timezone

from core.reagent.models import InventoryReagent, Reagent
from core.solution.models import Solution, SolutionStd, Standardization, StandardizationSolution, SolutionBase, SolutionStdBase

CONC = [('', '-----'), ('%', '%'), ('mg/L', 'mg/L'), ('M', 'M'), ('N', 'N')]
BOOLEAN = [(True, 'Si'), (False, 'No')]


# Creación de Soluciones
class SolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        solute_qs = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(), reagent__solvent=False, quantity_stock__gt=0, reagent__standard=False)
        self.fields['solute_reagent'].queryset = solute_qs
        self.fields['solute_reagent'].widget.attrs['data-reagents'] = {
            str(obj.id): str(obj.reagent.id) for obj in solute_qs
        }

        solvent_qs = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(), reagent__solvent=True, quantity_stock__gt=0, reagent__standard=False)
        self.fields['solvent_reagent'].queryset = solvent_qs
        self.fields['solvent_reagent'].widget.attrs['data-reagents'] = {
            str(obj.id): str(obj.reagent.id) for obj in solvent_qs
        }

        self.fields['solution_base'].queryset = SolutionBase.objects.filter(enable_solution=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'
        col_classes = {
            'code_solution': 'col-md-2',
            'concentration': 'col-md-2',
            'solution_base': 'col-md-4',
            'solute_reagent': 'col-md-6',
            'concentration_unit': 'col-md-2',
            'quantity_solution': 'col-md-2',
            'solvent_reagent': 'col-md-6',
            'standardizable': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')


    class Meta:
        model = Solution
        fields = [
            'code_solution', 'solution_base', 'solute_reagent', 'quantity_solution',
            'solvent_reagent', 'standardizable']
        widgets = {
            'code_solution': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'solute_reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'solvent_reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'standardizable': Select(attrs={'class': 'form-control', 'required': True}, choices=BOOLEAN),
            'solution_base': Select(attrs={'class': 'form-control', 'required': True}),
            'quantity_solution': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
        }

    def clean(self):
        """Validar datos y calcular cantidad de reactivo necesaria"""
        cleaned_data = super().clean()

        # Obtener campos necesarios
        solute_reagent = cleaned_data.get('solute_reagent')
        solution_base = cleaned_data.get('solution_base')
        concentration = cleaned_data.get('concentration')
        if not concentration and solution_base:
            concentration = solution_base.concentration_base
            cleaned_data['concentration'] = concentration

        concentration_unit = cleaned_data.get('concentration_unit')
        if not concentration_unit and solution_base:
            concentration_unit = solution_base.concentration_unit_base
            cleaned_data['concentration_unit'] = concentration_unit

        quantity_solution = cleaned_data.get('quantity_solution')

        # Validar correspondencia con la base
        if solution_base and solute_reagent:
            if solute_reagent.reagent_id != solution_base.solute_reagent_base_id:
                self.add_error('solute_reagent', f'El reactivo seleccionado ({solute_reagent.reagent.description_reagent}) no coincide con el definido en la base ({solution_base.solute_reagent_base.description_reagent})')

        # Si falta algún campo crítico, retornar sin validar más
        if not all([solute_reagent, concentration, concentration_unit, quantity_solution]):
            return cleaned_data

        # Validar valores numéricos positivos
        if concentration <= 0:
            self.add_error('concentration', 'La concentración debe ser mayor que cero')
            return cleaned_data

        if quantity_solution <= 0:
            self.add_error('quantity_solution', 'La cantidad de solución debe ser mayor que cero')
            return cleaned_data

        # Validar propiedades del reactivo soluto
        if not solute_reagent.purity:
            self.add_error('solute_reagent', 'El reactivo seleccionado no tiene pureza definida')
            return cleaned_data

        if not solute_reagent.density:
            self.add_error('solute_reagent', 'El reactivo seleccionado no tiene densidad definida')
            return cleaned_data

        # Obtener propiedades una sola vez
        purity = solute_reagent.purity
        density = solute_reagent.density
        reagent = solute_reagent.reagent
        sig_figs = reagent.sig_figs_solution

        # Calcular base común
        base_calc = quantity_solution * density

        # Calcular quantity_reagent según la unidad de concentración
        quantity_reagent = None

        try:
            if concentration_unit == '%':
                quantity_reagent = round(base_calc * (concentration / purity), sig_figs)

            elif concentration_unit == 'mg/L':
                quantity_reagent = round(base_calc * (concentration * purity / 10000), sig_figs)

            elif concentration_unit == 'M':
                if not reagent.molecular_weight:
                    self.add_error('solute_reagent', 'El reactivo seleccionado no tiene peso molecular registrado')
                    return cleaned_data
                factor = (concentration * reagent.molecular_weight) / (10 * purity)
                quantity_reagent = round(base_calc * factor, sig_figs)

            elif concentration_unit == 'N':
                if not reagent.gram_equivalent:
                    self.add_error('solute_reagent', 'El reactivo seleccionado no tiene equivalente gramo registrado')
                    return cleaned_data
                factor = (concentration * reagent.gram_equivalent) / (10 * purity)
                quantity_reagent = round(base_calc * factor, sig_figs)

        except Exception as e:
            self.add_error(None, f'Error al calcular la cantidad de reactivo: {str(e)}')
            return cleaned_data

        # Validar stock disponible
        if quantity_reagent is not None:
            if quantity_reagent > solute_reagent.quantity_stock:
                umb = reagent.umb
                error_message = (
                    f'La cantidad requerida ({quantity_reagent:.2f} {umb}) '
                    f'excede el stock disponible ({solute_reagent.quantity_stock:.2f} {umb})'
                )
                self.add_error('solute_reagent', error_message)
                return cleaned_data

            # Guardar el valor calculado para usarlo en save()
            cleaned_data['_quantity_reagent'] = quantity_reagent

        return cleaned_data

    def save(self, commit=True):
        """Guardar la instancia con los valores calculados"""
        instance = super().save(commit=False)

        instance.concentration = instance.solution_base.concentration_base
        instance.concentration_unit = instance.solution_base.concentration_unit_base

        # Usar el valor calculado en clean()
        if '_quantity_reagent' in self.cleaned_data:
            instance.quantity_reagent = self.cleaned_data['_quantity_reagent']
        else:
            solute_reagent = instance.solute_reagent
            purity = solute_reagent.purity
            density = solute_reagent.density
            sig_figs = solute_reagent.reagent.sig_figs_solution
            base_calc = instance.quantity_solution * density

            if instance.solution_base.concentration_unit_base == '%':
                instance.quantity_reagent = round(
                    base_calc * (instance.solution_base.concentration_base / purity),
                    sig_figs
                )
            elif instance.solution_base.concentration_unit_base == 'mg/L':
                instance.quantity_reagent = round(
                    base_calc * (instance.solution_base.concentration_base * purity / 10000),
                    sig_figs
                )
            elif instance.solution_base.concentration_unit_base == 'M':
                factor = (instance.solution_base.concentration_base * solute_reagent.reagent.molecular_weight) / (10 * purity)
                instance.quantity_reagent = round(base_calc * factor, sig_figs)
            elif instance.solution_base.concentration_unit_base == 'N':
                factor = (instance.solution_base.concentration_base * solute_reagent.reagent.gram_equivalent) / (10 * purity)
                instance.quantity_reagent = round(base_calc * factor, sig_figs)

        instance.quantity_solvent = float(instance.quantity_solution - instance.quantity_reagent)

        if commit:
            instance.save()

        return instance


# Creación de Soluciones Estándar
class SolutionStandardForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        solute_qs = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localdate(),
            reagent__solvent=False, quantity_stock__gt=0, reagent__standard=True).exclude(reagent__ready_to_use=True)
        self.fields['solute_std'].queryset = solute_qs
        self.fields['solute_std'].widget.attrs['data-reagents'] = {
            str(obj.id): str(obj.reagent.id) for obj in solute_qs
        }

        solvent_qs = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localdate(), reagent__solvent=True, quantity_stock__gt=0)
        self.fields['solvent_reagent'].queryset = solvent_qs
        self.fields['solvent_reagent'].widget.attrs['data-reagents'] = {
            str(obj.id): str(obj.reagent.id) for obj in solvent_qs
        }

        self.fields['solution_std_base'].queryset = SolutionStdBase.objects.filter(enable_solution_std=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStd
        fields = [
            'code_solution_std', 'solution_std_base', 'solute_std', 'concentration_std', 'concentration_unit', 'quantity_solution_std',
            'solvent_reagent']
        widgets = {
            'code_solution_std': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'solution_std_base': Select(attrs={'class': 'form-control', 'required': True}),
            'solute_std': Select(attrs={'class': 'form-control', 'required': True}),
            'solvent_reagent': Select(attrs={'class': 'form-control'}),
            'concentration_std': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'concentration_unit': Select(attrs={'class': 'form-control', 'required': True}, choices=CONC),
            'quantity_solution_std': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        solution_std_base = cleaned_data.get('solution_std_base')
        solute_std = cleaned_data.get('solute_std')

        concentration_std = cleaned_data.get('concentration_std')
        if not concentration_std and solution_std_base:
            concentration_std = solution_std_base.concentration_std_base
            cleaned_data['concentration_std'] = concentration_std

        concentration_unit = cleaned_data.get('concentration_unit')
        if not concentration_unit and solution_std_base:
            concentration_unit = solution_std_base.concentration_unit_base
            cleaned_data['concentration_unit'] = concentration_unit

        if solution_std_base and solute_std:
            if solute_std.reagent_id != solution_std_base.solute_std_base.reagent_id:
                self.add_error('solute_std', f'El estándar seleccionado ({solute_std.reagent.description_reagent}) no coincide con el definido en la base ({solution_std_base.solute_std_base.reagent.description_reagent})')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not instance.solute_std.purity:
            raise ValidationError('El reactivo seleccionado no tiene pureza definida')
        if not instance.solute_std.density:
            raise ValidationError('El reactivo seleccionado no tiene densidad definida')

        if not instance.solute_std.reagent.ready_to_use:
            if not instance.solute_std.reagent.volumetric:
                if instance.concentration_unit == '%':
                    instance.quantity_std = float(
                        instance.quantity_solution_std * (
                                instance.concentration_std / instance.solute_std.purity
                        ) * instance.solute_std.density
                    )
                elif instance.concentration_unit == 'mg/L':
                    instance.quantity_std = float(
                        instance.quantity_solution_std * (
                                instance.concentration_std / 10000 * instance.solute_std.purity
                        ) * instance.solute_std.density
                    )
                elif instance.concentration_unit == 'M':
                    if not instance.solute_std.reagent.molecular_weight:
                        raise ValidationError('El reactivo seleccionado no tiene peso molecular registrado')
                    instance.quantity_std = float(
                        instance.quantity_solution_std * (
                                (instance.concentration_std * instance.solute_std.reagent.molecular_weight) /
                                (10 * instance.solute_std.purity)
                        ) * instance.solute_std.density
                    )
                elif instance.concentration_unit == 'N':
                    if not instance.solute_std.reagent.gram_equivalent:
                        raise ValidationError('El reactivo seleccionado no tiene equivalente gramo registrado')
                    instance.quantity_std = float(
                        instance.quantity_solution_std * (
                                (instance.concentration_std * instance.solute_std.reagent.gram_equivalent) /
                                (10 * instance.solute_std.purity)
                        ) * instance.solute_std.density
                    )
            else:
                instance.quantity_std = (instance.quantity_solution_std * instance.concentration_std) / instance.solute_std.purity

            instance.quantity_solvent = float(instance.quantity_solution_std - instance.quantity_std)

        else:
            instance.concentration_std = float(instance.solute_std.purity)
            instance.concentration_unit = 'M'
            instance.quantity_solution_std = instance.solute_std.quantity_stock
            instance.quantity_std = instance.solute_std.quantity_stock
            instance.quantity_solvent = 0
            instance.expire_std_date_solution = instance.solute_std.date_expire

        # Validación de stock disponible
        if instance.quantity_std > instance.solute_std.quantity_stock:
            raise ValidationError(
                f'La cantidad requerida ({instance.quantity_std:.2f}) excede el stock disponible '
                f'({instance.solute_std.quantity_stock:.2f}) del reactivo seleccionado'
            )

        if commit:
            instance.save()

        return instance


# Confirmar preparación de Solución
class SolutionConfirmedForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preparation_confirmed'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Solution
        fields = ['preparation_confirmed']
        widgets = {'preparation_confirmed': Select(attrs={'class': 'form-control', 'hidden': True}),}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():

                instance = super().save(commit=False)
                user = get_current_user()

                instance.preparation_date = timezone.localdate()
                instance.preparation_confirmed = True
                instance.quantity_available_sln = instance.quantity_solution
                instance.preparated_by_id = user.id

                if instance.solute_reagent.reagent.stability_solution:
                    instance.expire_date_solution = instance.preparation_date + timedelta(
                        days=instance.solute_reagent.reagent.stability_solution)
                else:
                    raise ValidationError('El Reactivo no tiene definido Días Estabilidad en Solución')

                if commit:
                    instance.save()

                return instance
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Confirmar Solución Estándar
class SolutionStdConfirmedForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preparation_confirmed'].label = ''
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStd
        fields = ['preparation_confirmed']
        widgets = {'preparation_confirmed': Select(attrs={'class': 'form-control', 'hidden': True}),}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                instance = super().save(commit=False)
                user = get_current_user()

                instance.preparated_std_by_id = user.id
                instance.preparation_std_date = timezone.localdate()
                instance.preparation_confirmed = True

                if instance.solute_std.reagent.stability_solution:
                    instance.expire_std_date_solution = instance.preparation_std_date + timedelta(
                        days=instance.solute_std.reagent.stability_solution)
                else:
                    raise ValidationError('El Reactivo no tiene Días Estabilidad definido')

                if commit:
                    instance.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Registro de Estandarización
class StandardizationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.reagent = kwargs.pop('reagent')
        super().__init__(*args, **kwargs)
        self.fields['solution_std'].queryset = Reagent.objects.filter(standard=True, solvent=False, enable_reagent=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Standardization
        fields = ['solution_std', 'molar_relation']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'molar_relation': TextInput(attrs={'class': 'form-control', 'required': True})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.solution_reagent_id = self.reagent.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de Registro de Estandarización
class StandardizationUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solution_std'].queryset = Reagent.objects.filter(standard=True, solvent=False, enable_reagent=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Standardization
        fields = ['solution_std', 'molar_relation']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'molar_relation': TextInput(attrs={'class': 'form-control', 'required': True})
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


# Registro de Estandarización
class StandardizationSolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.std = kwargs.pop('std')
        self.sln = kwargs.pop('sln')
        super().__init__(*args, **kwargs)
        self.fields['quantity_standard'].label = str(self.std.solution_std.umb) + ' de Estándar'
        self.fields['standard_solution'].queryset = SolutionStd.objects.select_related('solute_std').filter(
            solute_std__reagent_id=self.std.solution_std.id, quantity_solution_std__gt=0)

        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = StandardizationSolution
        fields = ['standard_solution', 'quantity_standard', 'quantity_solution']
        widgets = {
            'standard_solution': Select(attrs={
                'class': 'form-control select2',
                'required': True,
                'style': 'width: 100%'
            }),
            'quantity_standard': TextInput(attrs={'class': 'form-control', 'required': True}),
            'quantity_solution': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        user = get_current_user()
        try:
            instance = super().save(commit=False)
            instance.solution_id = self.sln.id
            instance.standardized_by_id = user.id
            instance.standarization_date = timezone.localdate()

            aliquot = float(instance.quantity_standard)

            if self.sln.concentration_unit == 'M':
                mol_solute = (instance.quantity_solution * instance.standard_solution.concentration_std) / self.std.molar_relation
                instance.concentration_sln = round((mol_solute / aliquot), 3)
            elif self.sln.concentration_unit == 'N':
                eq_solute = instance.quantity_solution * instance.standard_solution.concentration_std
                instance.concentration_sln = round((eq_solute / aliquot), 3)

            if commit:
                instance.save()

            return instance
        except Exception as e:
            raise ValidationError({'error': str(e)})

    def clean(self):
        cleaned = super().clean()
        quantity_standard = cleaned.get('quantity_standard')
        stock_standard = cleaned.get('standard_solution').quantity_solution_std
        umb = self.std.solution_std.umb

        if quantity_standard > stock_standard:
            raise ValidationError(
                f'La cantidad requerida ({quantity_standard:.2f}{umb}) excede el stock disponible '
                f'({stock_standard:.2f}{umb}) del reactivo seleccionado'
            )

        return cleaned


# Configuración de Soluciones Base
class SolutionBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solute_reagent_base'].queryset = Reagent.objects.filter(enable_reagent=True, solvent=False, standard=False)
        self.fields['solvent_reagent_base'].queryset = Reagent.objects.filter(enable_reagent=True, solvent=True, standard=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'solute_reagent_base': 'col-md-4',
            'solvent_reagent_base': 'col-md-4',
            'concentration_base': 'col-md-2',
            'concentration_unit_base': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SolutionBase
        fields = ['solute_reagent_base', 'solvent_reagent_base', 'concentration_base', 'concentration_unit_base']
        widgets = {
            'solute_reagent_base': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'solvent_reagent_base': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'concentration_base': TextInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'concentration_unit_base': Select(attrs={'class': 'form-control'}, choices=CONC),
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


# Configuración de Soluciones Estándar Base
class SolutionStdBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solute_std_base'].queryset = Reagent.objects.filter(enable_reagent=True, solvent=False, standard=True)
        self.fields['solvent_reagent_base'].queryset = Reagent.objects.filter(enable_reagent=True, solvent=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        col_classes = {
            'solute_std_base': 'col-md-4',
            'solvent_reagent_base': 'col-md-4',
            'concentration_std_base': 'col-md-2',
            'concentration_unit_base': 'col-md-2',
        }

        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = SolutionStdBase
        fields = ['solute_std_base', 'solvent_reagent_base', 'concentration_std_base', 'concentration_unit_base']
        widgets = {
            'solute_std_base': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'solvent_reagent_base': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'concentration_std_base': TextInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'concentration_unit_base': Select(attrs={'class': 'form-control'}, choices=CONC),
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
