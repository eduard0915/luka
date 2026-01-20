from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DetailView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SpecificationProduct
from core.sampling.forms import SamplingAnalysisProcessingForm
from core.sampling.models import SamplingAnalysis, SamplingAnalysisProcessing
from core.solution.models import SolutionStd


# Detalle de Análisis de Muestra
class SamplingAnalysisDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SamplingAnalysis
    template_name = 'analysis_sampling/detail_sampling_analysis.html'
    permission_required = 'reagent.add_reagent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Procesamiento de Análisis de Muestra'
        context['entity'] = self.object
        context['analysis_processing'] = self.object.samplinganalysisprocessing_set.all()

        # Datos del método analítico
        method = self.object.analytical_method
        context['solutions'] = method.analyticalmethodsolution_set.all()
        context['std_solutions'] = method.analyticalmethodsolutionstd_set.all()
        context['reagents'] = method.analyticalmethodreagent_set.all()
        context['equipments'] = method.analyticalmethodequipment_set.all()
        context['materials'] = method.analyticalmethodmaterial_set.all()
        context['procedures'] = method.analyticalmethodprocedure_set.all()

        # Obtener la especificación del producto para este análisis
        sampling_process = self.object.sampling_process
        product = None
        if sampling_process.point_sampling:
            product = sampling_process.point_sampling.product
        elif sampling_process.group_sampling:
            product = sampling_process.group_sampling.sampling_point.product

        if product:
            specification = SpecificationProduct.objects.filter(
                product=product,
                method_test__analytical_method=method
            ).first()
            context['specification'] = specification

        context['icon'] = 'bi bi-calculator'
        context['back'] = reverse_lazy('sampling:detail_sampling_process', kwargs={'pk': self.object.sampling_process.id})
        # URL para agregar procesamiento
        context['create_processing_url'] = reverse_lazy('sampling:create_sampling_analysis_processing',
                                                       kwargs={'pk': self.object.id})
        return context


# Registro de Procesamiento de Análisis
class SamplingAnalysisProcessingCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingAnalysisProcessing
    form_class = SamplingAnalysisProcessingForm
    template_name = 'analysis_sampling/create_sampling_analysis_processing.html'
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
                    messages.success(request, '¡Procesamiento Registrado Satisfactoriamente!')
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        analysis = SamplingAnalysis.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'analysis': analysis})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Registro de Procesamiento de Análisis'
        return context


# Vista para Obtener la unidad de medida del reactivo
@login_required
@require_GET
def get_solution_std_unit(request):
    """Obtiene la unidad de medida del reactivo de la solución estándar"""
    try:
        solution_id = request.GET.get('solution_id')
        if not solution_id:
            return JsonResponse({'unit': None})

        solution = SolutionStd.objects.select_related(
            'solute_std__reagent'
        ).get(pk=solution_id)

        # Obtener la unidad de medida del reactivo
        unit = solution.solute_std.reagent.umb if solution.solute_std and solution.solute_std.reagent else None

        return JsonResponse({'unit': unit})
    except SolutionStd.DoesNotExist:
        return JsonResponse({'unit': None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
