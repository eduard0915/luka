from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from core.mixins import ValidatePermissionRequiredMixin
from core.solution.forms import StandarizationSolutionForm
from core.solution.models import StandarizationSolution, Solution


class StandarizationSolutionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = StandarizationSolution
    form_class = StandarizationSolutionForm
    template_name = 'standarization/create_std_sln.html'
    permission_required = 'reagent.add_reagent'

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sln = Solution.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'sln': sln})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Estandarización'
        return context
