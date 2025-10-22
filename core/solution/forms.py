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
            'concentration': TextInput(attrs={'class': 'form-control', 'required': True}),
            'concentration_unit': Select(attrs={'class': 'form-control', 'required': True}, choices=CONC),
            'quantity_solution': TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = get_current_user()

        instance.preparated_by_id = user.id
        instance.preparation_date = timezone.now()

        if instance.solute_reagent.reagent.stability_solution:
            instance.expire_date_solution = instance.preparation_date + timedelta(
                days=instance.solute_reagent.reagent.stability_solution)
        else:
            raise ValidationError('El Reactivo no tiene un Días Estabilidad definido')

        if instance.concentration_unit == '%':
            instance.quantity_reagent = float(instance.quantity_solution * (
                        instance.concentration / instance.solute_reagent.purity) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'mg/L':
            instance.quantity_reagent = float(instance.quantity_solution * (
                        instance.concentration / 10000 * instance.solute_reagent.purity) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'M':
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.molecular_weight) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)
        elif instance.concentration_unit == 'N':
            instance.quantity_reagent = float(instance.quantity_solution * (
                        (instance.concentration * instance.solute_reagent.reagent.gram_equivalent) / (
                            10 * instance.solute_reagent.purity)) * instance.solute_reagent.density)

        if commit:
            instance.save()

        return instance
