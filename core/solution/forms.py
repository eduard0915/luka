from datetime import timedelta

from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput
from django.utils import timezone

from core.reagent.models import InventoryReagent
from core.solution.models import Solution, StandarizationSolution, SolutionStd

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
            'code_solution', 'solute_reagent', 'concentration', 'concentration_unit', 'quantity_solution', 'solvent_reagent', 'standardizable']
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
            instance.quantity_reagent = float(instance.quantity_solution * (
                        instance.concentration / instance.solute_reagent.purity) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'mg/L':
            instance.quantity_reagent = float(instance.quantity_solution * (
                        instance.concentration / 10000 * instance.solute_reagent.purity) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'M':
            if not instance.solute_reagent.reagent.molecular_weight:
                raise ValidationError('El reactivo seleccionado no tiene peso molecular registrado')
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.molecular_weight) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'N':
            if not instance.solute_reagent.reagent.gram_equivalent:
                raise ValidationError('El reactivo seleccionado no tiene equivalente gramo registrado')
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.gram_equivalent) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)

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
            'solvent_reagent': Select(attrs={'class': 'form-control', 'required': True}),
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
                # data = form.save(commit=False)
                # data.preparation_std_date = timezone.localtime(timezone.now())
                #
                # if data.solute_std.reagent.stability_solution:
                #     data.expire_std_date_solution = data.preparation_std_date + timedelta(
                #         days=data.solute_std.reagent.stability_solution)
                # else:
                #     raise ValidationError('El Reactivo no tiene un Días Estabilidad definido')
                # data.save()
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
class StandarizationSolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.sln = kwargs.pop('sln')
        super().__init__(*args, **kwargs)
        self.fields['standard_sln'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            reagent__standard=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = StandarizationSolution
        fields = ['standard_sln', 'quantity_solution', 'quantity_standard']
        widgets = {
            'quantity_solution': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'quantity_standard': TextInput(attrs={'class': 'form-control', 'required': True, 'step': 'any'}),
            'standard_sln': Select(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        user = get_current_user()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.standarization_date = timezone.now()
                data.standardized_by_id = user.id
                data.concentration_sln = round(((data.quantity_standard * data.standard_sln.purity) / data.quantity_solution), data.standard_sln.reagent.sig_figs_solution)
                data.solution_id = self.sln.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
