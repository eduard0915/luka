"""Vistas para la gestión de procesos de muestreo."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView

from django.db.models import Q
from core.mixins import ValidatePermissionRequiredMixin
from core.product.models import SpecificationProduct
from core.sampling.forms import *
from core.sampling.models import SamplingProcess, SamplingAnalysis, SamplingAnalysisProcessingRelation
from core.utils import format_form_errors
from core.analytical_method.models import AnalyticalMethodCalculateRelation, AnalyticalMethodCalculate


class SamplingProcessCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de procesos de muestreo."""
    model = SamplingProcess
    form_class = SamplingProcessForm
    template_name = 'process_sampling/create_process_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_process')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación de proceso de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    messages.success(request, f'Proceso de Muestreo creado satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y configuración de creación al contexto."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Muestreo'
        context['title'] = 'Creación de Muestreo'
        context['div'] = '12'
        context['list_url'] = self.success_url
        return context


class SamplingProcessUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de procesos de muestreo."""
    model = SamplingProcess
    form_class = SamplingProcessForm
    template_name = 'process_sampling/create_process_sampling.html'
    success_url = reverse_lazy('sampling:list_sampling_process')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de proceso de muestreo."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    messages.success(request, f'Proceso de Muestreo editado satisfactoriamente!')
                else:
                    error_messages = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {error_messages}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega el título y configuración de edición al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Muestreo'
        context['entity'] = 'Edición de Muestreo'
        context['action'] = 'edit'
        context['div'] = '10'
        context['list_url'] = self.success_url
        return context


class SamplingProcessListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para el listado de procesos de muestreo."""
    model = SamplingProcess
    template_name = 'process_sampling/list_process_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa solicitudes POST para la búsqueda y filtrado de procesos."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                # Obtener el estado del filtro si existe
                status_filter = request.POST.get('status_filter', None)
                out_specification = request.POST.get('out_specification', None)

                user = get_current_user()
                
                qs = SamplingProcess.objects.select_related(
                    'group_sampling',
                    'point_sampling',
                    'sampling_created_by'
                ).filter(
                    Q(group_sampling__sampling_point__specification__product__site=user.laboratory.site) |
                    Q(sampling_point__specification__product__site=user.laboratory.site)
                )
                
                if status_filter:
                    qs = qs.filter(status_sampling=status_filter)

                if out_specification == 'True':
                    qs = qs.filter(samplinganalysis__comply='No Cumple').distinct()

                data = list(qs.values(
                    'id',
                    'group_sampling',
                    'group_sampling__sampling_point__sample_point_code',
                    'group_sampling__sampling_point__sample_point_name',
                    'group_sampling__sampling_point__product__description_product',
                    'date_sampling_scheduled',
                    'sampling_created_by__first_name',
                    'sampling_created_by__last_name',
                    'sampling_created_by__cargo',
                    'number_sample',
                    'point_sampling',
                    'point_sampling__sample_point_code',
                    'point_sampling__sample_point_name',
                    'point_sampling__product__description_product',
                    'status_sampling'
                ).order_by('-date_sampling'))

                # Formatea de campos
                for item in data:
                    if item['date_sampling_scheduled']:
                        item['date_sampling_scheduled'] = timezone.localtime(item['date_sampling_scheduled']).strftime('%Y-%m-%d %H:%M')
                    first_name = item.get('sampling_created_by__first_name', '') or ''
                    last_name = item.get('sampling_created_by__last_name', '') or ''
                    cargo = item.get('sampling_created_by__cargo', '') or ''
                    if first_name or last_name or cargo:
                        item['sampling_created_by__get_full_name'] = f"{first_name} {last_name}, {cargo}".strip()
                    else:
                        item['sampling_created_by__get_full_name'] = 'Automático'
                    if item['group_sampling']:
                        code_point = item.get('group_sampling__sampling_point__sample_point_code', '') or ''
                        name_point = item.get('group_sampling__sampling_point__sample_point_name', '') or ''
                        prod = item.get('group_sampling__sampling_point__product__description_product', '') or ''
                        item['group_sampling'] = f'{code_point} {name_point} - {prod}'.strip()
                    else:
                        code_point = item.get('point_sampling__sample_point_code', '') or ''
                        name_point = item.get('point_sampling__sample_point_name', '') or ''
                        prod = item.get('point_sampling__product__description_product', '') or ''
                        item['point_sampling'] = f'{code_point} {name_point} - {prod}'.strip()
                return JsonResponse(data, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Agrega el título, URL de creación y filtro de estado al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestreos'
        context['create_url'] = reverse_lazy('sampling:create_sampling_process')
        context['entity'] = 'Muestreos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-vials'
        context['status_filter'] = ''
        return context


class SamplingProcessScheduledListView(SamplingProcessListView):
    """Vista para el listado de muestreos programados."""

    def get_context_data(self, **kwargs):
        """Agrega el filtro de estado 'Programada' al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestreos Programados'
        context['entity'] = 'Muestreos Programados'
        context['status_filter'] = 'Programada'
        return context


class SamplingProcessConfirmedListView(SamplingProcessListView):
    """Vista para el listado de muestreos confirmados."""

    def get_context_data(self, **kwargs):
        """Agrega el filtro de estado 'Confirmada' al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestreos Confirmados'
        context['entity'] = 'Muestreos Confirmados'
        context['status_filter'] = 'Confirmada'
        return context


class SamplingProcessInProcessListView(SamplingProcessListView):
    """Vista para el listado de muestras en proceso."""

    def get_context_data(self, **kwargs):
        """Agrega el filtro de estado 'En Proceso' al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestras En Proceso'
        context['entity'] = 'Muestras En Proceso'
        context['status_filter'] = 'En Proceso'
        return context


class SamplingProcessOutSpecificationListView(SamplingProcessListView):
    """Vista para el listado de muestras fuera de especificación."""

    def get_context_data(self, **kwargs):
        """Agrega el filtro de fuera de especificación al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Muestras Fuera de Especificación'
        context['entity'] = 'Muestras Fuera de Especificación'
        context['status_filter'] = 'En Proceso'
        context['out_specification'] = 'True'
        return context


class SamplingProcessDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista para el detalle de un proceso de muestreo."""
    model = SamplingProcess
    template_name = 'process_sampling/detail_process_sampling.html'
    permission_required = 'reagent.add_reagent'

    def get_object(self, queryset=None):
        """Obtiene el proceso con las relaciones críticas precargadas."""
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.select_related(
            'group_sampling__sampling_point__product',
            'point_sampling__product'
        ).get(pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud de detalle del proceso."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega especificaciones, análisis, ecuaciones y cálculos al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle de Proceso de Muestreo'
        context['entity'] = self.object

        # Obtener el punto de muestreo y el producto asociado
        sampling_point = (
            self.object.group_sampling.sampling_point if self.object.group_sampling
            else self.object.point_sampling
        )
        product = sampling_point.product if sampling_point else None

        # Obtener especificaciones
        context['specifications'] = (
            sampling_point.specification.select_related('product', 'method_test__analytical_method').order_by('type_test', 'test_prod')
            if sampling_point else SpecificationProduct.objects.none()
        )

        # Obtener análisis y enriquecer con unidades de medida de SpecificationProduct
        sampling_analysis = SamplingAnalysis.objects.select_related('sampling_process', 'analytical_method').filter(
            sampling_process_id=self.object.id)
        
        # Mapear unidades de SpecificationProduct
        if sampling_point:
            specs = sampling_point.specification.all()
            # spec_units = {spec.method_test.analytical_method_id: spec.unit_measure for spec in specs}
            spec_units = {
                (spec.method_test or spec.method_test_relacional).analytical_method_id: spec.unit_measure
                for spec in specs
                if spec.method_test or spec.method_test_relacional
            }
            
            # También intentar obtener unidades de AnalyticalMethodCalculate si no están en SpecificationProduct
            method_ids = [sa.analytical_method_id for sa in sampling_analysis]
            calculates = AnalyticalMethodCalculate.objects.filter(analytical_method_id__in=method_ids)
            calculate_units = {c.analytical_method_id: c.unit_measure_calculate for c in calculates}
            
            for sa in sampling_analysis:
                sa.unit_measure_prod = spec_units.get(sa.analytical_method_id) or calculate_units.get(sa.analytical_method_id)
        
        context['sampling_analysis'] = sampling_analysis

        # Obtener los cálculos relacionales y generar la ecuación LaTeX siguiendo la lógica de ProductDetailView
        calcules_relation = AnalyticalMethodCalculateRelation.objects.select_related(
            'product', 'analytical_method_calculate'
        ).filter(product_id=product).order_by('date_creation')

        context['calcules_relation'] = calcules_relation

        # Obtener los cálculos realizados para esta muestra para filtrar las ecuaciones visibles
        processed_relations = SamplingAnalysisProcessingRelation.objects.filter(
            sampling_process_id=self.object.id
        ).values_list('analytical_method_calculate_relation__calculate_description_relation', flat=True)

        equations_data = {}
        current_desc = None
        for cr in calcules_relation:
            if cr.calculate_description_relation:
                current_desc = cr.calculate_description_relation
                if current_desc not in equations_data:
                    # Solo incluir si no ha sido procesado
                    if current_desc not in processed_relations:
                        equations_data[current_desc] = {'num': [], 'den': [], 'gen': [], 'unit': cr.unit_measure_calculate}
                    else:
                        # Si ya está procesado, marcar para saltar sus componentes
                        equations_data[current_desc] = None
            
            if not current_desc or equations_data.get(current_desc) is None:
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
            if data is None:
                continue
            str_num = r" \cdot ".join(data['num']) if data['num'] else "1"
            str_den = r" \cdot ".join(data['den']) if data['den'] else "1"
            str_gen = rf" \cdot {r' \cdot '.join(data['gen'])}" if data['gen'] else ""
            
            label = rf"\text{{{desc}}}"
            if data['unit']:
                label += rf" \text{{ ({data['unit']})}}"
            
            final_equations.append(rf"{label} = \frac{{{str_num}}}{{{str_den}}}{str_gen}")

        context['final_equations'] = final_equations

        context['result_calcule_relation'] = SamplingAnalysisProcessingRelation.objects.select_related(
            'analytical_method_calculate_relation'
        ).filter(
            sampling_process_id=self.kwargs.get('pk')
        )

        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('sampling:list_sampling_process')
        return context


class SamplingProcessImageUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para actualizar la foto de la muestra."""
    model = SamplingProcess
    form_class = SamplingProcessImageForm
    template_name = 'process_sampling/confirmation_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la actualización de la foto de la muestra."""
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Foto de la muestra actualizada satisfactoriamente!')
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y acción al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Actualizar Foto de la Muestra'
        context['action'] = 'edit'
        return context


class SamplingProcessConfirmedUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la confirmación de recepción de muestra."""
    model = SamplingProcess
    form_class = SamplingProcessConfirmedForm
    template_name = 'process_sampling/confirmation_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la confirmación de la muestra."""
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Muestra Confirmada satisfactoriamente!')
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y mensaje de confirmación al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Confirmación Toma de Muestra'
        context['info_form'] = mark_safe('<span class="text-danger me-2">¿Está seguro de confirmar la toma de la muestra?</span>')
        context['action'] = 'edit'
        return context


class SamplingProcessInProcessUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para cambiar el estado de la muestra a 'En Proceso'."""
    model = SamplingProcess
    form_class = SamplingProcessInProcessForm
    template_name = 'process_sampling/confirmation_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada y obtiene el objeto."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el cambio de estado de la muestra a 'En Proceso' y redirige al análisis si existe."""
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Inicio de Procesamiento de Muestra realizado satisfactoriamente!')
                analysis_id = self.kwargs.get('analysis_id')
                if analysis_id:
                    data['redirect_url'] = reverse_lazy('sampling:detail_sampling_analysis', kwargs={'pk': analysis_id})
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y mensaje de inicio de procesamiento al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Inicio de Procesamiento de Muestra'
        context['info_form'] = mark_safe('<span class="text-danger me-2">¿Está seguro de Iniciar Procesamiento de la Muestra?</span>')
        context['action'] = 'edit'
        return context


class SamplingProcessApprovedUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la aprobación del control de calidad de la muestra."""
    model = SamplingProcess
    form_class = SamplingProcessApprovedForm
    template_name = 'process_sampling/confirmation_sampling.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la solicitud con protección CSRF exceptuada."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la aprobación del control de calidad."""
        data = {}
        try:
            form = self.get_form()
            if form.is_valid():
                form.save()
                messages.success(request, f'Control de Calidad Aprobado satisfactoriamente!')
            else:
                error_messages = format_form_errors(form)
                messages.error(request, f'Por favor corrija los errores: {error_messages}')
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la entidad y mensaje de aprobación al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Aprobación de Control de Calidad Muestra'
        context['info_form'] = mark_safe('<span class="text-danger me-2">¿Está seguro de aprobar el control de calidad de la muestra?</span>')
        context['action'] = 'edit'
        return context
