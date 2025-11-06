from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.models import InventoryReagent
from core.solution.forms import SolutionStandardForm
from core.solution.models import SolutionStd


# Creación de Soluciones Estándar
class SolutionStandardCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SolutionStd
    form_class = SolutionStandardForm
    template_name = 'solution_std/create_solution_std.html'
    permission_required = 'reagent.add_reagent'

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
                    self.object = form.save()
                    code_solution = form.cleaned_data.get('code_solution')
                    messages.success(request, f'Solución Estándar "{code_solution}" creada satisfactoriamente!')
                    # Provide redirect URL to detail view for AJAX to use
                    data['redirect_url'] = self.get_success_url()
                else:
                    messages.error(request, form.errors)
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('solution:detail_solution_std', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparar Solución STD'
        context['action'] = 'add'
        context['entity'] = 'Preparar Solución Estándar'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        # Fallback cancel/back link to the solutions list
        try:
            context['list_url'] = reverse_lazy('solution:list_solution')
        except Exception:
            pass
        return context


# Detalle de Solución Estándar
class SolutionStdDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SolutionStd
    template_name = 'solution_std/detail_solution_std.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparación de Solución Estándar'
        context['entity'] = 'Preparación de Solución Estándar'
        context['label_url'] = reverse_lazy('solution:solution_label_pdf', kwargs={'pk': self.object.pk})
        # if self.request.user.has_perm('user.add_user'):
        #     context['back'] = reverse_lazy('user:user_list')
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution')
        context['update_solution'] = reverse_lazy('solution:update_solution', kwargs={'pk': self.object.pk})
        context['std'] = reverse_lazy('solution:create_solution_std', kwargs={'pk': self.object.pk})
        return context


@login_required
@require_http_methods(["GET"])
def get_inventory_reagent_data(request, reagent_id):
    """
    API endpoint para obtener datos de un reactivo del inventario
    """
    try:
        inventory_reagent = InventoryReagent.objects.select_related('reagent').get(id=reagent_id)

        data = {
            'id': str(inventory_reagent.id),
            'batch_number': inventory_reagent.batch_number,
            'purity': float(inventory_reagent.purity) if inventory_reagent.purity else None,
            'density': float(inventory_reagent.density) if inventory_reagent.density else None,
            'quantity_stock': float(inventory_reagent.quantity_stock) if inventory_reagent.quantity_stock else None,
            'date_expire': inventory_reagent.date_expire.isoformat() if inventory_reagent.date_expire else None,
            'reagent': {
                'id': str(inventory_reagent.reagent.id),
                'description': inventory_reagent.reagent.description_reagent,
                'code': inventory_reagent.reagent.code_reagent,
                'purity_unit': inventory_reagent.reagent.purity_unit,
                'molecular_weight': float(
                    inventory_reagent.reagent.molecular_weight) if inventory_reagent.reagent.molecular_weight else None,
                'gram_equivalent': float(
                    inventory_reagent.reagent.gram_equivalent) if inventory_reagent.reagent.gram_equivalent else None,
                'ready_to_use': inventory_reagent.reagent.ready_to_use,
                'stability_solution': inventory_reagent.reagent.stability_solution,
            }
        }
        return JsonResponse(data)
    except InventoryReagent.DoesNotExist:
        return JsonResponse({'error': 'Reactivo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
