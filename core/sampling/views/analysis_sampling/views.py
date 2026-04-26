from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
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
        # Agrupar relaciones de cálculo por descripción y generar LaTeX
        calculate_relations_all = method.analyticalmethodcalculaterelation_set.select_related(
            'analytical_method_calculate'
        ).all().order_by('date_creation')

        equations_data = {}
        current_desc = None
        for cr in calculate_relations_all:
            if cr.calculate_description_relation:
                current_desc = cr.calculate_description_relation
                if current_desc not in equations_data:
                    equations_data[current_desc] = {'num': [], 'den': [], 'gen': [], 'unit': cr.unit_measure_calculate}

            if not current_desc:
                continue

            parts = []
            if cr.analytical_method_calculate:
                parts.append(rf"\text{{{cr.analytical_method_calculate.calculate_description}}}")
            if cr.volumen_std:
                parts.append(str(cr.volumen_std))
            if cr.factor:
                parts.append(str(cr.factor))
            if cr.sample_quantity:
                parts.append(str(cr.sample_quantity))

            term = r" \cdot ".join(parts)
            if term:
                if cr.position == 'Numerador':
                    equations_data[current_desc]['num'].append(term)
                elif cr.position == 'Denominador':
                    equations_data[current_desc]['den'].append(term)
                elif cr.position == 'General':
                    equations_data[current_desc]['gen'].append(term)

        final_equations = []
        for desc, data in equations_data.items():
            str_num = r" \cdot ".join(data['num']) if data['num'] else "1"
            str_den = r" \cdot ".join(data['den']) if data['den'] else "1"
            str_gen = rf" \cdot {r' \cdot '.join(data['gen'])}" if data['gen'] else ""

            label = rf"\text{{{desc}}}"
            if data['unit']:
                label += rf" \text{{ ({data['unit']})}}"

            final_equations.append(rf"{label} = \frac{{{str_num}}}{{{str_den}}}{str_gen}")

        context['final_equations'] = final_equations

        # Mantener calculate_relations original para compatibilidad con botones de 'Calcular' si es necesario
        unique_relations = []
        descriptions_seen = set()
        for rel in calculate_relations_all:
            if rel.calculate_description_relation and rel.calculate_description_relation not in descriptions_seen:
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        analysis = SamplingAnalysis.objects.filter(pk=self.kwargs.get('pk')).first()
        relation = get_object_or_404(
            AnalyticalMethodCalculateRelation,
            pk=self.kwargs.get('pk_relation'),
            analytical_method=analysis.analytical_method,
        )

        all_rels = AnalyticalMethodCalculateRelation.objects.filter(
            product=relation.product,
            calculate_description_relation=relation.calculate_description_relation
        )

        numerator = 1.0
        denominator = 1.0
        has_num = False
        has_den = False

        for r in all_rels:
            if r.analytical_method_calculate:
                # Buscar el análisis del mismo proceso con el método correspondiente
                target_analysis = SamplingAnalysis.objects.filter(
                    sampling_process=analysis.sampling_process,
                    analytical_method=r.analytical_method_calculate.analytical_method
                ).first()
                
                # Usar average_concentration
                val = target_analysis.average_concentration if target_analysis and target_analysis.average_concentration else 0.0
                
                # Aplicar factor
                if r.factor:
                    val *= r.factor
                
                if r.position.lower() == 'numerador':
                    numerator *= val
                    has_num = True
                elif r.position.lower() == 'denominador':
                    denominator *= val
                    has_den = True

        if not has_num: numerator = 0.0
        if not has_den: denominator = 1.0

        form.initial['numerator'] = round(numerator, 4)
        form.initial['denominator'] = round(denominator, 4)
        
        sig_figs = analysis.analytical_method.sig_figs_result or 4
        if denominator != 0:
            form.initial['calcule'] = round(numerator / denominator, sig_figs)
        else:
            form.initial['calcule'] = 0
            
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
