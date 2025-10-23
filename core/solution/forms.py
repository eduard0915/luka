from datetime import timedelta

from crum import get_current_user
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, FileInput, Select, DateInput, NumberInput, CheckboxInput
from django.utils import timezone

from core.reagent.models import InventoryReagent
from core.solution.models import Solution


CONC = [('', '-----'), ('%', '%'), ('mg/L', 'mg/L'), ('M', 'M'), ('N', 'N')]


# Creación de Soluciones
class SolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solute_reagent'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.now(), reagent__solvent=False)
        self.fields['solvent_reagent'].queryset = InventoryReagent.objects.select_related('reagent').filter(
            date_expire__gte=timezone.now(), reagent__solvent=True)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Solution
        fields = ['code_solution', 'solute_reagent', 'concentration', 'concentration_unit', 'quantity_solution', 'solvent_reagent']
        widgets = {
            'code_solution': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'solute_reagent': Select(attrs={'class': 'form-control', 'required': True}),
            'solvent_reagent': Select(attrs={'class': 'form-control', 'required': True}),
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
                raise ValidationError('El reactivo seleccionado no tiene peso molecular definido')
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.molecular_weight) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'N':
            if not instance.solute_reagent.reagent.gram_equivalent:
                raise ValidationError('El reactivo seleccionado no tiene equivalente gramo definido')
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.gram_equivalent) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)

        if commit:
            instance.save()

        return instance


# Adición de Solvente
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
                data.preparation_date = timezone.now()

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
