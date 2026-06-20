from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView

from core.analytical_method.models import AnalyticalMethodCalculateRelation
from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SpecificationProduct, AnalyticalMethodProduct
from core.sampling.forms import SamplingAnalysisProcessingForm, SamplingAnalysisProcessingRelationForm, \
    SamplingAnalysisProcessingGravimetryForm, SamplingAnalysisForm
from core.sampling.models import *


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
            if cr.variable:
                parts.append(str(cr.variable))

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
        method = self.object.analytical_method
        specification = None
        sampling_point = None

        if sampling_process.point_sampling:
            sampling_point = sampling_process.point_sampling
        elif sampling_process.group_sampling:
            sampling_point = sampling_process.group_sampling.sampling_point

        if sampling_point:
            # Buscar la especificación en el punto de muestreo que coincida con el método
            specification = sampling_point.specification.filter(
                method_test__analytical_method=method
            ).first()

        # Si no se encuentra en el punto de muestreo, intentar por el producto
        if not specification:
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
        if self.object.analytical_method.type_method == 'Volumetrico':
            context['create_processing_url'] = reverse_lazy('sampling:sampling_analysis_volumetry', kwargs={'pk': self.object.id})
        elif self.object.analytical_method.type_method == 'Gravimetrico':
            context['create_processing_url'] = reverse_lazy('sampling:sampling_analysis_gravimetry', kwargs={'pk': self.object.id})
        return context


# Registro de Procesamiento de Análisis Volumétrico
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


# Registro de Procesamiento de Análisis Gravimétrico
class SamplingAnalysisProcessingGravimetryCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingAnalysisProcessing
    form_class = SamplingAnalysisProcessingGravimetryForm
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
        context['entity'] = 'Registro de Procesamiento de Análisis Gravimétrico'
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
                    messages.success(request, '¡Procesamiento de Calculo de Variables Realizado Satisfactoriamente!')
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        analysis = SamplingAnalysis.objects.filter(sampling_process=self.kwargs.get('pk')).first()
        sampling = SamplingProcess.objects.get(pk=self.kwargs.get('pk'))

        product = None
        if sampling.point_sampling:
            product = sampling.point_sampling.product
        elif sampling.group_sampling:
            product = sampling.group_sampling.sampling_point.product

        relation = AnalyticalMethodCalculateRelation.objects.select_related(
            'analytical_method_calculate'
        ).filter(
            product=product,
            calculate_description_relation__isnull=False,
            analytical_method_calculate__isnull=True
        ).first()

        kwargs.update({
            'analysis': analysis,
            'sampling': sampling,
            'relation': relation
        })
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        analysis_qs = SamplingAnalysis.objects.filter(sampling_process=self.kwargs.get('pk'))
        sampling = SamplingProcess.objects.get(pk=self.kwargs.get('pk'))

        product = None
        if sampling.point_sampling:
            product = sampling.point_sampling.product
        elif sampling.group_sampling:
            product = sampling.group_sampling.sampling_point.product

        # Validar que existe un producto
        if not product:
            return form

        # Obtener relaciones de cálculo como QuerySet
        relation_num_qs = AnalyticalMethodCalculateRelation.objects.select_related(
            'analytical_method_calculate'
        ).filter(
            product=product,
            position='Numerador',
            analytical_method_calculate__isnull=False
        )

        relation_den_qs = AnalyticalMethodCalculateRelation.objects.select_related(
            'analytical_method_calculate'
        ).filter(
            product=product,
            position='Denominador',
            analytical_method_calculate__isnull=False
        )

        # Inicializar variables
        numerator = 1.0
        denominator = 1.0
        has_num = False
        has_den = False

        # Procesar numerador
        for relation_num in relation_num_qs:
            if relation_num.analytical_method_calculate:
                # Obtener el análisis correspondiente
                target_analysis = analysis_qs.filter(
                    analytical_method=relation_num.analytical_method_calculate.analytical_method
                ).first()

                if target_analysis and target_analysis.average_concentration:
                    val = float(target_analysis.average_concentration)
                    if relation_num.factor:
                        val *= relation_num.factor
                    numerator *= val
                    has_num = True

        # Procesar denominador
        for relation_den in relation_den_qs:
            if relation_den.analytical_method_calculate:
                # Obtener el análisis correspondiente
                target_analysis = analysis_qs.filter(
                    analytical_method=relation_den.analytical_method_calculate.analytical_method
                ).first()

                if target_analysis and target_analysis.average_concentration:
                    val = float(target_analysis.average_concentration)
                    if relation_den.factor:
                        val *= relation_den.factor
                    denominator *= val
                    has_den = True

        # Establecer valores por defecto si no se encontraron
        if not has_num:
            numerator = 0.0
        if not has_den:
            denominator = 1.0

        # Asignar valores al formulario
        form.initial['numerator'] = round(numerator, 4)
        form.initial['denominator'] = round(denominator, 4)

        # Calcular el resultado
        sig_figs = analysis_qs.first().analytical_method.sig_figs_result if analysis_qs.exists() else 4
        if denominator != 0:
            form.initial['calcule'] = round(numerator / denominator, sig_figs)
        else:
            form.initial['calcule'] = 0

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'

        sampling = SamplingProcess.objects.get(pk=self.kwargs.get('pk'))

        product = None
        if sampling.point_sampling:
            product = sampling.point_sampling.product
        elif sampling.group_sampling:
            product = sampling.group_sampling.sampling_point.product

        # Obtener la primera relación de cálculo si existe
        relation = None
        if product:
            relation = AnalyticalMethodCalculateRelation.objects.filter(
                product_id=product.id,
                analytical_method_calculate__isnull=False
            ).first()

        # Usar la relación solo si existe
        if relation:
            context['entity'] = f'Calcular {relation.calculate_description_relation}'
        else:
            context['entity'] = 'Cálculo Relacional'

        context['confirm_msg'] = '¿Está Seguro de Ejecutar el Calculo?'
        context['detail_button'] = 'Si, Ejecutar'
        return context


# Eliminación de cálculo de variables relacionadas
class SamplingAnalysisProcessingRelationDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = SamplingAnalysisProcessingRelation
    template_name = 'analysis_sampling/delete_analysis.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            detail = self.object.analytical_method_calculate_relation.calculate_description_relation
            self.object.delete()
            messages.success(request, f'Cálculo de {detail} eliminado satisfactoriamente!')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar de Calculo'
        context['delete'] = 'Está seguro de eliminar calculo de parametro?'
        context['info_delete'] = f'{self.object.analytical_method_calculate_relation.calculate_description_relation}'
        return context


class SamplingAnalysisListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SamplingAnalysis
    template_name = 'analysis_sampling/list_analysis.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'searchdata':
                data = []
                for i in SamplingAnalysis.objects.all().select_related(
                    'sampling_process',
                    'sampling_process__group_sampling',
                    'sampling_process__group_sampling__sampling_point',
                    'sampling_process__point_sampling',
                    'analytical_method'
                ):
                    data.append(i.toJSON())
            elif action == 'delete':
                pk = request.POST.get('id')
                obj = SamplingAnalysis.objects.get(pk=pk)
                obj.delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Análisis de Muestras'
        context['create_url'] = reverse_lazy('sampling:create_sampling_analysis')
        context['list_url'] = reverse_lazy('sampling:list_sampling_analysis')
        context['entity'] = 'Análisis de Muestras'
        return context


class SamplingAnalysisCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SamplingAnalysis
    form_class = SamplingAnalysisForm
    template_name = 'analysis_sampling/create_analysis.html'
    success_url = reverse_lazy('sampling:list_sampling_analysis')
    permission_required = 'reagent.add_reagent'

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Método de Analisis Asociado Satisfactoriamente!')
                    data['success'] = True
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(request, error)
                            else:
                                messages.error(request, f"{field}: {error}")
                    data['success'] = False
                    data['errors'] = form.errors
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sampling_process = SamplingProcess.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'sampling_process': sampling_process})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Asociar Método de Analísis'
        context['action'] = 'add'
        return context


class SamplingAnalysisDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = SamplingAnalysis
    template_name = 'analysis_sampling/delete_analysis.html'
    success_url = reverse_lazy('sampling:list_sampling_analysis')
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminación de Método de Análisis de Muestra'
        context['info_delete'] = f'¿Está seguro de eliminar el método de análisis "{self.object.analytical_method}"?'
        return context

