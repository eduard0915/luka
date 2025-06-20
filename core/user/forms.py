from django.forms import *

from core.user.models import *

SELECT = [(True, 'Si'), (False, 'No')]


# Creación de usuario
class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].label = 'Perfil'
        self.fields['email'].label = 'E-mail'
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'cargo', 'cellphone', 'cedula', 'username', 'password', 'groups', 'site'
        ]
        widgets = {
            'password': PasswordInput(render_value=True, attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': EmailInput(attrs={'class': 'form-control', 'required': True}),
            'cargo': TextInput(attrs={'class': 'form-control'}),
            'cellphone': TextInput(attrs={'class': 'form-control'}),
            'cedula': TextInput(attrs={'class': 'form-control'}),
            'username': TextInput(attrs={'class': 'form-control'}),
            'groups': SelectMultiple(attrs={'class': 'form-control', 'required': True}),
            'site': Select(attrs={'class': 'form-control', 'required': True}),
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_staff', 'is_active']
        help_texts = {
            'groups': 'Seleccione perfil del usuario',
            'is_active': 'Indica si el usuario está habilitado',
            'username': 'Únicamente letras y/o números'
        }


    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                pwd = self.cleaned_data['password']
                u = form.save(commit=False)
                if u.pk is None:
                    u.set_password(pwd)
                else:
                    user = User.objects.get(pk=u.pk)
                    if user.password != pwd:
                        u.set_password(pwd)
                u.save()
                u.groups.clear()
                for g in self.cleaned_data['groups']:
                    u.groups.add(g)
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de usuario por administrador
class UserUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].label = 'Perfil'
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'cargo', 'cellphone', 'cedula', 'username', 'site', 'groups']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': EmailInput(attrs={'class': 'form-control', 'required': True}),
            'cargo': TextInput(attrs={'class': 'form-control'}),
            'cellphone': TextInput(attrs={'class': 'form-control'}),
            'cedula': TextInput(attrs={'class': 'form-control'}),
            'username': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'groups': SelectMultiple(attrs={'class': 'form-control', 'required': True}),
            'site': Select(attrs={'class': 'form-control', 'required': True}),
            # 'photo': FileInput(attrs={'class': 'form-control-file'})

        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_staff']

        help_texts = {
            'groups': 'Seleccione perfil del usuario',
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


# Creación de capacitación
class TrainingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Training
        fields = ['description_training', 'training_by', 'date_training', 'support_training']
        widgets = {
            'description_training': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'training_by': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_training': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'date_training': DateInput(attrs={'class': 'form-control', 'type': 'date'})

        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.user_id = self.user.id
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de capacitación
class TrainingUptadeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Training
        fields = ['description_training', 'training_by', 'date_training', 'support_training']
        widgets = {
            'description_training': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'training_by': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_training': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'date_training': DateInput(attrs={'class': 'form-control', 'type': 'date'})

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
