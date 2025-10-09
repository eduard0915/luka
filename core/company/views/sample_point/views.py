from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView

from core.company.forms import SamplePointForm, SamplePointUpdateForm
from core.company.models import SamplePoint, Site
from core.mixins import ValidatePermissionRequiredMixin


# Creación de Puntos de Muestreo
class SamplePointCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplePoint
    form_class = SamplePointForm
    template_name = 'sample_point/create_sample_point.html'
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
                    messages.success(request, f'Punto de Muestreo creado satisfactoriamente!')
                else:
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        site = Site.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'site': site})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Punto de Muestreo'
        return context


# Edición de Puntos de Muestreo
class SamplePointUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = SamplePoint
    form_class = SamplePointUpdateForm
    template_name = 'sample_point/create_sample_point.html'
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
                    messages.success(request, f'Punto de Muestreo editado satisfactoriamente!')
                else:
                    messages.error(request, 'Por favor corrija los errores: {}'.format(form.errors.as_json()))
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sample = SamplePoint.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'sample': sample})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Edición de Punto de Muestreo'
        context['action'] = 'edit'
        return context
