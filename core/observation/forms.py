"""Formularios de la aplicación de observaciones.

Define el formulario para la creación y edición de observaciones.
"""  # noqa: E501

from django.forms import ModelForm, Textarea
from crum import get_current_user
from core.observation.models import Observation


class ObservationForm(ModelForm):
    """Formulario para crear y editar una observación."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario desactivando el autocompletado de campos."""
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Observation
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su comentario',
                'rows': 3,
                'cols': 3
            }),
        }

    def save(self, commit=True):
        """Guarda la observación asignando el usuario autenticado como autor del comentario."""
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                user = get_current_user()
                if user:
                    data.comment_by = user
                if commit:
                    data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
