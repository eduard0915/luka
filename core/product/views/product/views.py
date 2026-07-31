"""Vistas para el CRUD de productos y su detalle con información relacionada.

Incluye la creación, edición, listado y detalle de productos, así como
la construcción de ecuaciones para los cálculos dependientes.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.forms import ProductForm
from core.product.models import Product, SamplePoint, AnalyticalMethodProduct, SpecificationProduct
from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation, DependentCalculation
from core.sampling.models import SamplingGroup
from core.utils import format_form_errors


# Creación de Productos
class ProductCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de un nuevo producto."""

    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    permission_required = 'reagent.add_reagent'
    url_redirect = reverse_lazy('product:list_product')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Inicializa el objeto en None y procesa la petición sin CSRF."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la creación del producto vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                    messages.success(request, f'Producto creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        """Retorna la URL de redirección al detalle del producto creado."""
        return reverse('product:detail_product', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Agrega los datos de contexto específicos para la creación de producto."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Producto'
        context['title'] = 'Creación de Producto'
        context['div'] = '8'
        context['list_url'] = self.url_redirect
        return context


# Edición de Productos
class ProductUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para la edición de un producto existente."""

    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('product:list_product')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene el objeto actual y procesa la petición sin CSRF."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la edición del producto vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    messages.success(request, f'Producto editado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega los datos de contexto específicos para la edición de producto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Punto de Muestreo'
        context['entity'] = 'Edición de Punto de Muestreo'
        context['action'] = 'edit'
        context['div'] = '8'
        context['list_url'] = self.success_url
        return context


# Listado de Productos
class ProductListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para el listado de productos con búsqueda vía AJAX."""

    model = Product
    template_name = 'product/list_product.html'
    permission_required = 'reagent.view_inventoryreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la petición HTTP con protección CSRF desactivada."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Retorna los datos de productos en formato JSON para la tabla del listado."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Product.objects.all().order_by('-date_creation'):
                    data.append({
                        'id': i.id,
                        'code_product': i.code_product,
                        'description_product': i.description_product,
                        'enable_product': i.enable_product,
                        'version': i.version,
                        'site': i.site.site_name
                    })
                return JsonResponse(data, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Agrega los datos de contexto para la plantilla del listado."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['create_url'] = reverse_lazy('product:create_product')
        context['entity'] = 'Productos'
        context['div'] = '9'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Detalle de Producto
def _build_relation_equation(relations):
    """Construye la ecuación LaTeX a partir de un conjunto de relaciones de cálculo.

    Retorna None si no existe una descripción de cálculo entre las relaciones.
    """
    num_terms_rel = []
    den_terms_rel = []
    gen_terms_rel = []
    rel_desc = ""
    rel_unit = ""

    for cr in relations:
        parts_rel = []
        if cr.calculate_description_relation:
            rel_desc = cr.calculate_description_relation
            rel_unit = cr.unit_measure_calculate
        if cr.analytical_method_calculate:
            term = f"\\text{{{cr.analytical_method_calculate.calculate_description}}}"
            if cr.analytical_method_calculate.unit_measure_calculate:
                term += f" \\text{{ ({cr.analytical_method_calculate.unit_measure_calculate})}}"
            parts_rel.append(term)
        if cr.calculate_relation_related:
            term = f"\\text{{{cr.calculate_relation_related.calculate_description_relation}}}"
            if cr.calculate_relation_related.unit_measure_calculate:
                term += f" \\text{{ ({cr.calculate_relation_related.unit_measure_calculate})}}"
            parts_rel.append(term)
        if cr.volumen_std:
            parts_rel.append(f"\\text{{{cr.volumen_std}}}")
        if cr.factor:
            parts_rel.append(str(cr.factor))
        if cr.sample_quantity:
            parts_rel.append(f"\\text{{{cr.sample_quantity}}}")

        item_text_rel = " \\times ".join(parts_rel)
        if not item_text_rel:
            continue

        if cr.position == 'Numerador':
            num_terms_rel.append(item_text_rel)
        elif cr.position == 'Denominador':
            den_terms_rel.append(item_text_rel)
        elif cr.position == 'General':
            gen_terms_rel.append(item_text_rel)

    if not rel_desc:
        return None

    str_num_rel = " \\times ".join(num_terms_rel) if num_terms_rel else "1"
    str_den_rel = " \\times ".join(den_terms_rel) if den_terms_rel else ""
    str_gen_rel = f" \\times {' \\times '.join(gen_terms_rel)}" if gen_terms_rel else ""

    label_rel = f"\\text{{{rel_desc}}}"
    if rel_unit:
        label_rel += f" \\text{{ ({rel_unit})}}"
    if str_den_rel:
        return f"{label_rel} = \\frac{{{str_num_rel}}}{{{str_den_rel}}}{str_gen_rel}"
    return f"{label_rel} = {str_num_rel}{str_gen_rel}"


class ProductDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista de detalle de producto con puntos de muestreo, métodos, especificaciones y ecuaciones."""

    model = Product
    template_name = 'product/detail_product.html'
    permission_required = 'equipment.add_equipmentinstrumental'

    def dispatch(self, request, *args, **kwargs):
        """Procesa la petición HTTP para mostrar el detalle del producto."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Construye el contexto con las relaciones del producto y la ecuación de cálculo."""
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.code_product
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('product:list_product')
        context['create_sample_point'] = reverse_lazy('product:create_sample_point', kwargs={'pk': self.object.pk})
        context['sample_point'] = SamplePoint.objects.select_related('product').filter(
            enable_point=True, product_id=self.object.id).order_by('sequence')
        context['sampling_groups'] = SamplingGroup.objects.select_related(
            'sampling_point__product'
        ).filter(
            sampling_point__product_id=self.object.id
        ).order_by('sampling_point__sequence')
        context['create_sampling_group'] = reverse_lazy('sampling:create_sampling_group_product', kwargs={'pk': self.object.pk})
        context['create_method_product'] = reverse_lazy('product:create_method_product', kwargs={'pk': self.object.pk})
        context['analytical_methods'] = AnalyticalMethodProduct.objects.select_related('product').filter(product_id=self.object.id)
        context['create_specification_product'] = reverse_lazy('product:create_specification_product', kwargs={'pk': self.object.pk})
        context['create_specification_product_calcule'] = reverse_lazy('product:create_specification_product_calcule', kwargs={'pk': self.object.pk})
        context['specifications'] = SpecificationProduct.objects.select_related(
            'method_test__analytical_method',
            'method_test_relacional'
        ).filter(product_id=self.object.id)
        context['specification_rel'] = SpecificationProduct.objects.select_related('method_test__analytical_method').filter(product_id=self.object.id).first()
        calcules_relation = AnalyticalMethodCalculateRelation.objects.select_related('product').filter(product_id=self.object.id).order_by('-date_creation')
        context['calcules_relation'] = calcules_relation
        context['has_relations'] = calcules_relation.exists()
        dependent_calculations = DependentCalculation.objects.filter(product_id=self.object.id).order_by('consecutive')
        context['dependent_calculations'] = dependent_calculations
        context['create_dependent_calculation'] = reverse_lazy('product:add_dependent_calculation', kwargs={'pk': self.object.pk})
        first_dep = dependent_calculations.first()
        context['first_dependent_calculation'] = first_dep
        deps_with_description = set(AnalyticalMethodCalculateRelation.objects.filter(
            consecutive_calcule__in=dependent_calculations,
            calculate_description_relation__isnull=False
        ).values_list('consecutive_calcule_id', flat=True))
        context['deps_with_description'] = deps_with_description
        deps_with_sample_gram = set(AnalyticalMethodCalculateRelation.objects.filter(
            consecutive_calcule__in=dependent_calculations,
            sample_quantity__isnull=False
        ).values_list('consecutive_calcule_id', flat=True))
        context['deps_with_sample_gram'] = deps_with_sample_gram
        calcules_by_dep = {}
        for dep in dependent_calculations:
            dep_calcules = [cr for cr in calcules_relation if cr.consecutive_calcule_id == dep.id]
            if dep_calcules:
                calcules_by_dep[dep.id] = dep_calcules
        context['calcules_by_dep'] = calcules_by_dep

        if calcules_relation.exists():
            context['final_equation_relation'] = _build_relation_equation(calcules_relation)

        equations_by_dep = {}
        for dep_id, dep_calcules in calcules_by_dep.items():
            equation = _build_relation_equation(dep_calcules)
            if equation:
                equations_by_dep[dep_id] = equation
        context['equations_by_dep'] = equations_by_dep

        return context


# Vistas para Cálculos Dependientes de Productos
