from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.company.forms import ProcessForm, ProcessUpdateForm
from core.company.models import Process, Site
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Proceso
class ProcessCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Process
    form_class = ProcessForm
    template_name = 'process/create_process.html'
    permission_required = 'company.add_company'

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
                    messages.success(request, f'Proceso creado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'site': Site.objects.get(pk=self.kwargs.get('pk'))})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Proceso'
        context['class'] = 'col-md-8'
        return context


# Edición de Proceso
class ProcessUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Process
    form_class = ProcessUpdateForm
    template_name = 'process/create_process.html'
    permission_required = 'company.add_company'

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
                    messages.success(request, f'Proceso editado satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                # return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Proceso'
        context['action'] = 'edit'
        return context
