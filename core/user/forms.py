from datetime import timedelta

from django.forms import *

from core.company.models import Company
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
            'first_name', 'last_name', 'email', 'cargo', 'cellphone', 'cedula', 'username', 'password', 'groups', 'site', 'photo'
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
            'photo': FileInput(attrs={'class': 'form-control-file'})
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_staff', 'is_active']
        help_texts = {
            'groups': 'Seleccione perfil del usuario',
            'is_active': 'Indica si el usuario está habilitado',
            'username': 'Únicamente letras y/o números',
            'photo': 'Opcional, máximo 256Kb .jpg .png',
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
class UserUpdateAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].label = 'Perfil'
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'cargo', 'cellphone', 'cedula', 'username', 'site', 'groups', 'photo']
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
            'photo': FileInput(attrs={'class': 'form-control-file'})

        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_staff']

        help_texts = {
            'groups': 'Seleccione perfil del usuario',
            'photo': 'Opcional, máximo 256Kb .jpg .png',
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


# Edición de usuario
class UserUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'cargo', 'cellphone', 'cedula', 'username', 'photo']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': EmailInput(attrs={'class': 'form-control', 'required': True}),
            'cargo': TextInput(attrs={'class': 'form-control'}),
            'cellphone': TextInput(attrs={'class': 'form-control'}),
            'cedula': TextInput(attrs={'class': 'form-control'}),
            'username': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'photo': FileInput(attrs={'class': 'form-control-file'})

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


# Reseteo de contraseña de usuario por administrador
class UserPasswordUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = 'password',
        widgets = {
            'password': PasswordInput(render_value=False, attrs={'class': 'form-control'}),
        }
        help_texts = {
            'password': 'Reseteo de contraseña de usuario'
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
        fields = ['description_training', 'training_by', 'date_training', 'date_training_expire', 'support_training']
        widgets = {
            'description_training': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'training_by': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_training': FileInput(attrs={'class': 'form-control', 'type': 'file', 'required': True}),
            'date_training': DateInput(attrs={'class': 'form-control', 'type': 'text', 'required': True, 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'}),
            'date_training_expire': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        company = Company.objects.first()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.user_id = self.user.id
                data.date_training_alert = (data.date_training_expire - timedelta(days=company.training_alert))
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Actualización de capacitación
class TrainingCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.training = kwargs.pop('training')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Training
        fields = ['training_by', 'date_training', 'date_training_expire', 'support_training']
        widgets = {
            'training_by': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_training': FileInput(attrs={'class': 'form-control', 'type': 'file', 'required': True}),
            'date_training': DateInput(attrs={'class': 'form-control', 'type': 'text', 'required': True, 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'}),
            'date_training_expire': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'})
        }

    def save(self, commit=True):
        data = {}
        form = super()
        company = Company.objects.first()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.description_training = str(self.training.description_training)
                data.user_id = self.training.user.id
                data.date_training_alert = (data.date_training_expire - timedelta(days=company.training_alert))
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Edición de capacitación
class TrainingUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Training
        fields = ['description_training', 'training_by', 'date_training', 'date_training_expire', 'support_training']
        widgets = {
            'description_training': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'training_by': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_training': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'date_training': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd', 'required': True}),
            'date_training_expire': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'})

        }

    def save(self, commit=True):
        data = {}
        form = super()
        company = Company.objects.first()
        try:
            if form.is_valid():
                data = form.save(commit=False)
                data.date_training_alert = (data.date_training_expire - timedelta(days=company.training_alert))
                data.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data


# Creación de competencia
class CompetenceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Competence
        fields = ['description_competence', 'institution', 'date_competence', 'support_competence']
        widgets = {
            'description_competence': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'institution': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_competence': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'date_competence': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'})

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


# Edición de competencia
class CompetenceUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Competence
        fields = ['description_competence', 'institution', 'date_competence', 'support_competence']
        widgets = {
            'description_competence': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'institution': TextInput(attrs={'class': 'form-control', 'required': True, 'type': 'text'}),
            'support_competence': FileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'date_competence': DateInput(attrs={'class': 'form-control', 'type': 'text', 'data-datepicker': '1', 'placeholder': 'yyyy-mm-dd'})

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
