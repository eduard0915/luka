from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DetailView

from core.analytical_method.models import AnalyticalMethodCalculateRelation, AnalyticalMethodCalculate
from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SpecificationProduct
from core.sampling.forms import SamplingAnalysisProcessingForm, SamplingAnalysisProcessingRelationForm
from core.sampling.models import SamplingAnalysis, SamplingAnalysisProcessing, SamplingAnalysisProcessingRelation
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
        context['analysis_processing'] = self.object.samplinganalysisprocessing_set.filter(relational_calculation=False).order_by('-analyzed_date')
        context['analysis_processing_relational'] = self.object.samplinganalysisprocessing_set.filter(relational_calculation=True).order_by('-analyzed_date')
        context['analysis_processing_relational_new'] = self.object.samplinganalysisprocessingrelation_set.all().order_by('-date_creation')
        context['analysis_count'] = self.object.samplinganalysisprocessing_set.filter(relational_calculation=False).count()

        # Datos del método analítico
        method = self.object.analytical_method
        context['solutions'] = method.analyticalmethodsolution_set.all()
        context['std_solutions'] = method.analyticalmethodsolutionstd_set.all()
        context['reagents'] = method.analyticalmethodreagent_set.all()
        context['equipments'] = method.analyticalmethodequipment_set.all()
        context['materials'] = method.analyticalmethodmaterial_set.all()
        context['procedures'] = method.analyticalmethodprocedure_set.all()
        # Agrupar relaciones de cálculo por descripción para evitar duplicados en el template
        calculate_relations_all = method.analyticalmethodcalculaterelation_set.all()
        unique_relations = []
        descriptions_seen = set()
        for rel in calculate_relations_all:
            if rel.calculate_description_relation not in descriptions_seen:
                unique_relations.append(rel)
                descriptions_seen.add(rel.calculate_description_relation)
        context['calculate_relations'] = unique_relations

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
        context['create_processing_url'] = reverse_lazy(
            'sampling:create_sampling_analysis_processing', kwargs={'pk': self.object.id})
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


# Registro de Procesamiento de Análisis Relacional
class SamplingAnalysisProcessingRelationCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingAnalysisProcessingRelation
    form_class = SamplingAnalysisProcessingRelationForm
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
                    messages.success(request, '¡Procesamiento Relacional Registrado Satisfactoriamente!')
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        analysis = get_object_or_404(SamplingAnalysis, pk=self.kwargs.get('pk'))
        relation = get_object_or_404(
            AnalyticalMethodCalculateRelation,
            pk=self.kwargs.get('pk_relation'),
            analytical_method=analysis.analytical_method
        )

        kwargs.update({
            'analysis': analysis,
            'relation': relation
        })
        return kwargs

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     analysis = SamplingAnalysis.objects.get(pk=self.kwargs.get('pk'))
    #     calcule = AnalyticalMethodCalculate.objects.get(pk=self.kwargs.get('pk_calcule'))
    #     relation = AnalyticalMethodCalculateRelation.objects.filter(analytical_method_calculate_id=analysis.analytical_method.id).first()
    #
    #     kwargs.update({
    #         'analysis': analysis,
    #         'relation': relation
    #     })
    #     return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        analysis = get_object_or_404(SamplingAnalysis, pk=self.kwargs.get('pk'))
        relation = get_object_or_404(
            AnalyticalMethodCalculateRelation,
            pk=self.kwargs.get('pk_relation'),
            analytical_method=analysis.analytical_method
        )

        all_relations = AnalyticalMethodCalculateRelation.objects.select_related('analytical_method').filter(
            analytical_method_id=analysis.analytical_method.id,
            calculate_description_relation=relation.calculate_description_relation
        )
        var_num = all_relations.filter(position__iexact='Numerador')
        var_den = all_relations.filter(position__iexact='Denominador')

        base_processing = SamplingAnalysisProcessing.objects.filter(
            sample_analysis_id=analysis.id,
            relational_calculation=False
        ).first()

        if not base_processing:
            base_processing = SamplingAnalysisProcessing.objects.filter(
                sample_analysis__sampling_process_id=analysis.sampling_process_id,
                relational_calculation=False
            ).order_by('-analyzed_date').first()

        if base_processing:
            qty_std = float(base_processing.quantity_standard)
            qty_sample = float(base_processing.quantity_sample)

            def calculate_part(relations, target_pos=None):
                factor = 1
                sample = 1
                std = 1
                relation_val = 1
                used_prev = False
                for r in relations:
                    if r.factor is not None:
                        factor *= float(r.factor)
                    if r.sample_quantity and r.sample_quantity.strip():
                        sample = float(qty_sample)
                    if r.volumen_std is not None:
                        std = qty_std
                    
                    # 1. Prioridad: Cálculo específico definido en la relación
                    if r.analytical_method_calculate is not None:
                        prev_processing = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=analysis.sampling_process_id,
                            analytical_method_calculate=r.analytical_method_calculate,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()
                        if prev_processing:
                            relation_val *= prev_processing.concentration_sample
                            used_prev = True
                
                # 2. Si no se encontró por cálculo específico, buscar por posición (ej. Denominador)
                if not used_prev and target_pos:
                    prev_processing_pos = SamplingAnalysisProcessing.objects.filter(
                        sample_analysis__sampling_process_id=analysis.sampling_process_id,
                        analytical_method_calculate__position__iexact=target_pos,
                        relational_calculation=False
                    ).order_by('-analyzed_date').first()
                    if prev_processing_pos:
                        relation_val = prev_processing_pos.concentration_sample
                        used_prev = True

                # 3. Fallback final al procesamiento base
                if not used_prev:
                    if base_processing:
                        relation_val = base_processing.concentration_sample
                
                return std * factor * sample * relation_val

            if 'numerator' in form.fields:
                val_num = calculate_part(var_num, 'Numerador')
                form.initial['numerator'] = val_num
                form.fields['numerator'].initial = val_num
            if 'denominator' in form.fields:
                val_den = calculate_part(var_den, 'Denominador')
                form.initial['denominator'] = val_den
                form.fields['denominator'].initial = val_den

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        relation = get_object_or_404(AnalyticalMethodCalculateRelation, pk=self.kwargs.get('pk_relation'))
        context['entity'] = f'Calcular {relation.calculate_description_relation}'
        # context['confirm_msg'] = '¿Está Seguro de Ejecutar el Calculo?'
        context['detail_button'] = 'Si, Ejecutar'
        context['relation'] = relation
        return context


# Vista para Obtener la unidad de medida del reactivo
# @login_required
# @require_GET
# def get_solution_std_unit(request):
#     """Obtiene la unidad de medida del reactivo de la solución estándar"""
#     try:
#         solution_id = request.GET.get('solution_id')
#         if not solution_id:
#             return JsonResponse({'unit': None})
#
#         solution = SolutionStd.objects.select_related(
#             'solute_std__reagent'
#         ).get(pk=solution_id)
#
#         # Obtener la unidad de medida del reactivo
#         unit = solution.solute_std.reagent.umb if solution.solute_std and solution.solute_std.reagent else None
#
#         return JsonResponse({'unit': unit})
#     except SolutionStd.DoesNotExist:
#         return JsonResponse({'unit': None})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)
