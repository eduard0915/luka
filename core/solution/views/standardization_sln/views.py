from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.solution.forms import StandardizationSolutionForm
from core.solution.models import StandardizationSolution, Standardization, Solution


# Registro de Estandarización
class StandardizationSolutionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = StandardizationSolution
    form_class = StandardizationSolutionForm
    template_name = 'standardization_sln/create_standardization_sln.html'
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
                    messages.success(request, '¡Estandarización Registrada Satisfactoriamente!')
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
        std = Standardization.objects.get(solution_reagent_id=sln.solute_reagent.reagent.id)
        kwargs.update({'std': std, 'sln': sln})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Estandarización'
        return context


# Eliminación de Estandarización
class StandardizationSolutionDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = StandardizationSolution
    template_name = 'standardization_sln/delete_standardization_sln.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Registro de Estandarización Eliminado Satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar de Registro'
        context['delete'] = 'Está seguro de eliminar la Estandarización?'
        return context
