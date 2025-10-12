from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import UserForm, UserUpdateAdminForm, UserUpdateForm, UserPasswordUpdateForm
from core.user.models import User, Training, Competence


# Creación de usuario
class UserCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'user/create_user.html'
    success_url = reverse_lazy('user:user_list')
    permission_required = 'user.add_user'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    name_username = form.cleaned_data.get('username')
                    messages.success(request, f'Usuario "{name_username}" creado satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de Usuarios'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Usuario'
        context['div'] = '10'
        context['icon'] = 'bi bi-person-add'
        return context


# Listado de usuarios
class UserListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = User
    template_name = 'user/list_user.html'
    permission_required = 'user.add_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                usuarios = list(User.objects.select_related('site').values(
                    'id',
                    'date_joined',
                    'last_login',
                    'cedula',
                    'username',
                    'cargo',
                    'groups__name',
                    'email',
                    'is_active',
                    'first_name',
                    'last_name',
                    'slug',
                    'site__site_name',
                ).filter(is_superuser=False).order_by('first_name'))
                return JsonResponse(usuarios, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Usuarios'
        context['create_url'] = reverse_lazy('user:user_create')
        context['entity'] = 'Usuarios'
        context['div'] = '11'
        context['icon'] = 'bi bi-people'
        return context


# Edición de usuario por Administrador
class UserUpdateAdminView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateAdminForm
    template_name = 'user/create_user.html'
    success_url = reverse_lazy('user:user_list')
    permission_required = 'user.change_user'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    name_username = form.cleaned_data.get('username')
                    messages.success(request, f'Usuario "{name_username}" actualizado satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Usuarios'
        context['list_url'] = self.success_url
        context['entity'] = 'Edición Usuario'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'bi bi-person-fill-gear'
        return context


# Edición de usuario
class UserUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/create_user.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    name_username = form.cleaned_data.get('username')
                    messages.success(request, f'Usuario "{name_username}" actualizado satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(slug=self.kwargs.get('slug'))
        context['title'] = 'Edición de Usuarios'
        context['entity'] = 'Edición Usuario'
        context['action'] = 'edit'
        context['div'] = '11'
        context['icon'] = 'bi bi-person-fill-gear'
        context['list_url'] = reverse_lazy('user:user_detail', kwargs={'slug': user.slug})       
        return context


# Detalle de Usuario
class UserDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = User
    template_name = 'user/detail_user.html'
    permission_required = 'user.view_user'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        now = timezone.now()
        Training.objects.filter(
            training_status='Vigente',
            date_training_expire__lte=now
        ).update(training_status='Vencido')
        return super(UserDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Perfil de Usuario'
        context['entity'] = 'Perfil de Usuario'
        context['group_user'] = User.objects.values('groups__name').filter(slug=self.kwargs['slug'])
        context['training'] = Training.objects.filter(user__slug=self.kwargs['slug']).order_by('-date_training')
        context['competence'] = Competence.objects.filter(user__slug=self.kwargs['slug']).order_by('-date_competence')
        if self.request.user.has_perm('user.add_user'):
            context['back'] = reverse_lazy('user:user_list')
        context['icon'] = 'bi bi-person-vcard'
        return context


# Cambio de contraseña por usuario
class UserChangePasswordView(LoginRequiredMixin, ValidatePermissionRequiredMixin, FormView):
    model = User
    form_class = PasswordChangeForm
    template_name = 'user/change_password.html'
    permission_required = 'user.view_user'
    success_url = reverse_lazy('user:change_password')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = PasswordChangeForm(user=self.request.user)
        form.fields['old_password'].widget.attrs['class'] = 'form-control'
        form.fields['new_password1'].widget.attrs['class'] = 'form-control'
        form.fields['new_password2'].widget.attrs['class'] = 'form-control'
        return form

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = PasswordChangeForm(user=request.user, data=request.POST)
                if form.is_valid():
                    form.save()
                    update_session_auth_hash(request, form.user)
                    messages.success(request, f'Su contraseña fue actualizada satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambio de Contraseña'
        context['list_url'] = self.success_url
        context['entity'] = 'Cambio de Contraseña'
        context['action'] = 'edit'
        context['div'] = '4'
        context['icon'] = 'bi bi-shield-lock'
        return context

# Reseteo de contraseña por administrador
class UserPasswordUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'user/change_password.html'
    success_url = reverse_lazy('user:user_list')
    permission_required = 'user.change_user'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Contraseña de usuario reseteada satisfactoriamente!')
                    data['success'] = True
                else:
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reseteo de Contraseña'
        context['list_url'] = self.success_url
        context['entity'] = 'Reseteo de Contraseña de Usuario'
        context['action'] = 'edit'
        context['div'] = '4'
        context['icon'] = 'bi bi-shield-lock'
        return context
