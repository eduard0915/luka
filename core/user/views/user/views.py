from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import *
from core.user.models import User


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
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
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
        context['icon'] = 'person_add'
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
        return context


# Edición de usuario por Administrador
class UserUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
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
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
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
        context['icon'] = 'person_edit'
        return context


# Detalle de Usuario por administrador
class UserDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = User
    template_name = 'user/detail_user.html'
    permission_required = 'user.change_user'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super(UserDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Perfil de Usuario'
        context['entity'] = 'Perfil de Usuario'
        context['group_user'] = User.objects.values('groups__name').filter(slug=self.kwargs['slug'])
        context['training'] = Training.objects.filter(user__slug=self.kwargs['slug']).order_by('-date_training')
        return context
