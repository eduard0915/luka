from datetime import timedelta

from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput
from django.utils import timezone

from core.reagent.models import InventoryReagent, Reagent
from core.solution.models import Solution, SolutionStd, Standardization, StandardizationSolution

CONC = [('', '-----'), ('%', '%'), ('mg/L', 'mg/L'), ('M', 'M'), ('N', 'N')]
BOOLEAN = [(True, 'Si'), (False, 'No')]


# Creación de Soluciones
class SolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solute_reagent'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(timezone.now()), reagent__solvent=False, quantity_stock__gt=0, reagent__standard=False)
        self.fields['solvent_reagent'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(timezone.now()), reagent__solvent=True, quantity_stock__gt=0, reagent__standard=False)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Solution
        fields = [
            'code_solution', 'solute_reagent', 'concentration', 'concentration_unit', 'quantity_solution',
            'solvent_reagent', 'standardizable']
        widgets = {
            'code_solution': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'solute_reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'solvent_reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'standardizable': Select(attrs={'class': 'form-control', 'required': True}, choices=BOOLEAN),
            'concentration': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'concentration_unit': Select(attrs={'class': 'form-control', 'required': True}, choices=CONC),
            'quantity_solution': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = get_current_user()

        instance.preparated_by_id = user.id

        # Validar que los campos necesarios no sean None
        if not instance.solute_reagent.purity:
            raise ValidationError('El reactivo seleccionado no tiene pureza definida')
        if not instance.solute_reagent.density:
            raise ValidationError('El reactivo seleccionado no tiene densidad definida')

        if instance.concentration_unit == '%':
            instance.quantity_reagent = round((instance.quantity_solution * (
                    instance.concentration / instance.solute_reagent.purity) * instance.solute_reagent.density),
                                              instance.solute_reagent.reagent.sig_figs_solution)
        elif instance.concentration_unit == 'mg/L':
            instance.quantity_reagent = round((instance.quantity_solution * (
                    instance.concentration / 10000 * instance.solute_reagent.purity) * instance.solute_reagent.density),
                                              instance.solute_reagent.reagent.sig_figs_solution)
        elif instance.concentration_unit == 'M':
            if not instance.solute_reagent.reagent.molecular_weight:
                raise ValidationError('El reactivo seleccionado no tiene peso molecular registrado')
            instance.quantity_reagent = round((instance.quantity_solution * (
                    (instance.concentration * instance.solute_reagent.reagent.molecular_weight) / (
                    10 * instance.solute_reagent.purity)) * instance.solute_reagent.density),
                                              instance.solute_reagent.reagent.sig_figs_solution)
        elif instance.concentration_unit == 'N':
            if not instance.solute_reagent.reagent.gram_equivalent:
                raise ValidationError('El reactivo seleccionado no tiene equivalente gramo registrado')
            instance.quantity_reagent = round((instance.quantity_solution * (
                    (instance.concentration * instance.solute_reagent.reagent.gram_equivalent) / (
                    10 * instance.solute_reagent.purity)) * instance.solute_reagent.density),
                                              instance.solute_reagent.reagent.sig_figs_solution)

        # Validación de stock disponible
        if instance.quantity_reagent > instance.solute_reagent.quantity_stock:
            raise ValidationError(
                f'La cantidad requerida ({instance.quantity_reagent:.2f}) excede el stock disponible '
                f'({instance.solute_reagent.quantity_stock:.2f}) del reactivo seleccionado'
            )

        if commit:
            instance.save()

        return instance


# Creación de Soluciones Estándar
class SolutionStandardForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solute_std'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(timezone.now()), reagent__solvent=False, quantity_stock__gt=0, reagent__standard=True)
        self.fields['solvent_reagent'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.localtime(timezone.now()), reagent__solvent=True, quantity_stock__gt=0)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStd
        fields = [
            'code_solution_std', 'solute_std', 'concentration_std', 'concentration_unit', 'quantity_solution_std',
            'solvent_reagent']
        widgets = {
            'code_solution_std': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'solute_std': Select(attrs={'class': 'form-control', 'required': True}),
            'solvent_reagent': Select(attrs={'class': 'form-control'}),
            'concentration_std': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'concentration_unit': Select(attrs={'class': 'form-control', 'required': True}, choices=CONC),
            'quantity_solution_std': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = get_current_user()

        instance.preparated_std_by_id = user.id
        instance.preparation_std_date = timezone.localtime(timezone.now())

        # Validar que los campos necesarios no sean None
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


# Adición de Solvente a Solución
class SolutionAddSolventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Solution
        fields = ['quantity_solvent']
        widgets = {'quantity_solvent': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.preparation_date = timezone.localtime(timezone.now())

                if data.solute_reagent.reagent.stability_solution:
                    data.expire_date_solution = data.preparation_date + timedelta(
                        days=data.solute_reagent.reagent.stability_solution)
                else:
                    raise ValidationError('El Reactivo no tiene un Días Estabilidad definido')
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Adición de Solvente a Solución Estándar
class SolutionStdAddSolventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SolutionStd
        fields = ['quantity_solvent']
        widgets = {'quantity_solvent': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),}

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                instance = super().save(commit=False)
                instance.preparation_std_date = timezone.localtime(timezone.now())

                if instance.solute_std.reagent.stability_solution:
                    instance.expire_std_date_solution = instance.preparation_std_date + timedelta(
                        days=instance.solute_std.reagent.stability_solution)
                else:
                    raise ValidationError('El Reactivo no tiene un Días Estabilidad definido')

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
        fields = ['solution_std', 'quantity_aliquot', 'molar_relation']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'quantity_aliquot': TextInput(attrs={'class': 'form-control', 'required': True}),
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
        fields = ['solution_std', 'quantity_aliquot', 'molar_relation']
        widgets = {
            'solution_std': Select(attrs={'class': 'form-control select2', 'required': True, 'style': 'width: 100%'}),
            'quantity_aliquot': TextInput(attrs={'class': 'form-control', 'required': True}),
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
        self.fields['standard_sln'].queryset = SolutionStd.objects.filter(
            solute_std__reagent_id=self.std.solution_std_id, quantity_solution_std__gt=0)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = StandardizationSolution
        fields = ['standard_sln', 'quantity_standard']
        widgets = {
            'standard_sln': Select(attrs={
                'class': 'form-control select2',
                'required': True,
                'style': 'width: 100%'
            }),
            'quantity_standard': TextInput(attrs={
                'class': 'form-control',
                'required': True
            })
        }

    def save(self, commit=True):
        user = get_current_user()
        try:
            instance = super().save(commit=False)
            instance.solution_id = self.sln.id
            instance.quantity_aliquot = float(self.std.quantity_aliquot)
            instance.standardized_by_id = user.id
            instance.standarization_date = timezone.localtime(timezone.now())

            if self.sln.concentration_unit == 'M':
                mol_solute = instance.quantity_standard * instance.standard_sln.concentration_std / self.std.molar_relation
                instance.concentration_sln = round((mol_solute / self.std.quantity_aliquot), 3)
            elif self.sln.concentration_unit == 'N':
                eq_solute = instance.quantity_standard * instance.standard_sln.concentration_std
                instance.concentration_sln = round((eq_solute / self.std.quantity_aliquot), 3)

            if commit:
                instance.save()

            return instance
        except Exception as e:
            raise ValidationError({'error': str(e)})
