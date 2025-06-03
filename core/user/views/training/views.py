from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from core.mixins import ValidatePermissionRequiredMixin
from core.user.forms import TrainingForm
from core.user.models import Training, User


# Registro de capacitación
class TrainingCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'training/create_training.html'
    permission_required = 'user.view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Capacitación Registrada Satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     user = User.objects.get(slug=self.kwargs.get('slug'))
    #     print(user)
    #     kwargs.update({'user': user})
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Capacitación'
        # user = User.objects.get(slug=self.kwargs.get('slug'))

        # context['field_number'] = 4
        # context['field_width'] = 3
        # context['act'] = reverse_lazy('user:create_training', kwargs={'pk': user.slug})
        return context
