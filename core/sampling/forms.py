from django.forms import ModelForm, TextInput, Select, TimeInput, CheckboxInput
from core.sampling.models import SamplingGroup

class SamplingGroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = SamplingGroup
        fields = ['sampling_point', 'hour_sampling', 'number_sampling_day', 'enable_sampling_group']
        widgets = {
            'sampling_point': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
            'hour_sampling': TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
            'number_sampling_day': TextInput(attrs={'class': 'form-control', 'type': 'number'}),
            'enable_sampling_group': CheckboxInput(attrs={'class': 'form-check-input'}),
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
