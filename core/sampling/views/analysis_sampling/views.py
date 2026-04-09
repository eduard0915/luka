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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # analysis = get_object_or_404(SamplingAnalysis, pk=self.kwargs.get('pk'))
        analysis = SamplingAnalysis.objects.filter(pk=self.kwargs.get('pk')).order_by('-date_creation').first()
        relation = get_object_or_404(
            AnalyticalMethodCalculateRelation,
            pk=self.kwargs.get('pk_relation'),
            analytical_method=analysis.analytical_method,
        )

        # Asignar a variables usadas en calculate_part
        var_num_rel = AnalyticalMethodCalculateRelation.objects.filter(
            analytical_method_id=analysis.analytical_method.id,
            position__iexact='Numerador'
        ).order_by('date_creation')

        var_den_rel = AnalyticalMethodCalculateRelation.objects.filter(
            analytical_method_id=analysis.analytical_method.id,
            position__iexact='Denominador'
        ).order_by('date_creation')

        all_base_calculates = AnalyticalMethodCalculate.objects.filter(
            analytical_method_id=analysis.analytical_method.id
        ).order_by('date_creation')

        var_num_base = all_base_calculates.filter(position__iexact='Numerador')
        var_den_base = all_base_calculates.filter(position__iexact='Denominador')

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
            qty_std = float(base_processing.concentration_sample)
            qty_sample = float(base_processing.quantity_sample)

            def calculate_part(relations_rel, relations_base, target_pos=None):
                total_product = 1.0
                has_elements = False

                # Procesar Relaciones (AMCR)
                for r in relations_rel:
                    has_elements = True
                    factor = 1.0
                    sample = 1.0
                    std = 1.0
                    relation_val = 1.0
                    used_prev = False

                    if r.factor is not None:
                        factor = float(r.factor)
                    if r.sample_quantity and r.sample_quantity.strip():
                        sample = float(qty_sample)
                    if r.volumen_std is not None:
                        std = qty_std
                    
                    # 1. Prioridad: Cálculo específico definido en la relación (misma muestra)
                    if r.analytical_method_calculate is not None:
                        prev_processing = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis_id=analysis.id,
                            analytical_method_calculate=r.analytical_method_calculate,
                            relational_calculation=False
                        ).first()
                        
                        # Si no se encuentra en la misma muestra, buscar en el proceso de muestreo
                        if not prev_processing:
                            prev_processing = SamplingAnalysisProcessing.objects.filter(
                                sample_analysis__sampling_process_id=analysis.sampling_process_id,
                                analytical_method_calculate=r.analytical_method_calculate,
                                relational_calculation=False
                            ).order_by('-analyzed_date').first()

                        if prev_processing:
                            relation_val = prev_processing.concentration_sample
                            used_prev = True
                    
                    # 2. Búsqueda por posición en la misma muestra
                    if not used_prev and target_pos:
                        prev_processing_pos = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis_id=analysis.id,
                            analytical_method_calculate__position__iexact=target_pos,
                            relational_calculation=False
                        ).first()

                        # Si no se encuentra, buscar en el proceso de muestreo
                        if not prev_processing_pos:
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
                    
                    total_product *= (std * factor * sample * relation_val)

                # Procesar Cálculos Base (AMC)
                for b in relations_base:
                    has_elements = True
                    factor = 1.0
                    sample = 1.0
                    std = 1.0
                    
                    if b.factor is not None:
                        factor = float(b.factor)
                    if b.sample_quantity and b.sample_quantity.strip():
                        sample = float(qty_sample)
                    if b.volumen_std is not None:
                        std = qty_std
                    
                    # Para el cálculo base, el valor es el del procesamiento base actual o último
                    val = 1.0
                    
                    # Buscar primero en la misma muestra
                    prev_base = SamplingAnalysisProcessing.objects.filter(
                        sample_analysis_id=analysis.id,
                        analytical_method_calculate=b,
                        relational_calculation=False
                    ).first()

                    # Si no se encuentra, buscar en el proceso de muestreo
                    if not prev_base:
                        prev_base = SamplingAnalysisProcessing.objects.filter(
                            sample_analysis__sampling_process_id=analysis.sampling_process_id,
                            analytical_method_calculate=b,
                            relational_calculation=False
                        ).order_by('-analyzed_date').first()

                    if prev_base:
                        val = float(prev_base.concentration_sample)
                    elif base_processing:
                        val = float(base_processing.concentration_sample)

                    total_product *= (std * factor * sample * val)

                return total_product if has_elements else 0.0

            if 'numerator' in form.fields:
                val_num = calculate_part(var_num_rel, var_num_base, 'Numerador')
                form.initial['numerator'] = val_num
                # form.fields['numerator'].initial = val_num
            if 'denominator' in form.fields:
                val_den = calculate_part(var_den_rel, var_den_base, 'Denominador')
                form.initial['denominator'] = val_den
                # form.fields['denominator'].initial = val_den

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
