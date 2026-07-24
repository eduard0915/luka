"""Vistas para el registro y eliminación de estandarizaciones de soluciones."""

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
    """Vista para registrar una estandarización de solución contra un estándar."""
    model = StandardizationSolution
    form_class = StandardizationSolutionForm
    template_name = 'standardization_sln/create_standardization_sln.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición de registro de estandarización."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de estandarización vía AJAX."""
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
        """Agrega los objetos de estandarización y solución a los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        sln = Solution.objects.get(pk=self.kwargs.get('pk'))
        std = Standardization.objects.get(solution_reagent_id=sln.solute_reagent.reagent.id)
        kwargs.update({'std': std, 'sln': sln})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega la acción y entidad al contexto."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Estandarización'
        return context


# Eliminación de Estandarización
class StandardizationSolutionDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    """Vista para eliminar un registro de estandarización de solución."""
    model = StandardizationSolution
    template_name = 'standardization_sln/delete_standardization_sln.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        """Obtiene el registro de estandarización a eliminar y maneja la petición."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Elimina el registro de estandarización vía AJAX."""
        data = {}
        try:
            self.object.delete()
            messages.success(request, 'Registro de Estandarización Eliminado Satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y el mensaje de confirmación de eliminación."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar de Registro'
        context['delete'] = 'Está seguro de eliminar la Estandarización?'
        return context
