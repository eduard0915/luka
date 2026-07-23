from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from core.mixins import ValidatePermissionRequiredMixin
from core.product.forms import ProductForm
from core.product.models import Product, SamplePoint, AnalyticalMethodProduct, SpecificationProduct
from core.analytical_method.models import AnalyticalMethodCalculate, AnalyticalMethodCalculateRelation
from core.utils import format_form_errors


# Creación de Productos
class ProductCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('product:list_product')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

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
                    form.save()
                    data['success'] = True
                    data['redirect_url'] = str(self.success_url)
                    messages.success(request, f'Producto creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
                    messages.error(request, f'Por favor corrija los errores: {data["error"]}')
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'add'
        context['entity'] = 'Creación de Producto'
        context['title'] = 'Creación de Producto'
        context['div'] = '8'
        context['list_url'] = self.success_url
        return context


# Edición de Productos
class ProductUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    success_url = reverse_lazy('product:list_product')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de Punto de Muestreo'
        context['entity'] = 'Edición de Punto de Muestreo'
        context['action'] = 'edit'
        context['div'] = '8'
        context['list_url'] = self.success_url
        return context


# Listado de Productos
class ProductListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Product
    template_name = 'product/list_product.html'
    permission_required = 'reagent.view_inventoryreagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['create_url'] = reverse_lazy('product:create_product')
        context['entity'] = 'Productos'
        context['div'] = '9'
        context['icon'] = 'fa-solid fa-vial-virus'
        return context


# Detalle de Producto
class ProductDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Product
    template_name = 'product/detail_product.html'
    permission_required = 'equipment.add_equipmentinstrumental'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.code_product
        context['entity'] = self.object
        context['icon'] = 'bi bi-file-earmark-ruled'
        context['back'] = reverse_lazy('product:list_product')
        context['create_sample_point'] = reverse_lazy('product:create_sample_point', kwargs={'pk': self.object.pk})
        context['sample_point'] = SamplePoint.objects.select_related('product').filter(
            enable_point=True, product_id=self.object.id).order_by('sequence')
        context['create_method_product'] = reverse_lazy('product:create_method_product', kwargs={'pk': self.object.pk})
        context['analytical_methods'] = AnalyticalMethodProduct.objects.select_related('product').filter(product_id=self.object.id)
        context['create_specification_product'] = reverse_lazy('product:create_specification_product', kwargs={'pk': self.object.pk})
        context['create_specification_product_calcule'] = reverse_lazy('product:create_specification_product_calcule', kwargs={'pk': self.object.pk})
        context['specifications'] = SpecificationProduct.objects.select_related(
            'method_test__analytical_method',
            'method_test_relacional'
        ).filter(product_id=self.object.id)

        calcules_relation = AnalyticalMethodCalculateRelation.objects.select_related('product').filter(product_id=self.object.id).order_by('-date_creation')
        context['calcules_relation'] = calcules_relation
        context['has_relations'] = calcules_relation.exists()

        if calcules_relation.exists():
            num_terms_rel = []
            den_terms_rel = []
            gen_terms_rel = []
            rel_desc = ""
            rel_unit = ""

            for cr in calcules_relation:
                parts_rel = []
                if cr.calculate_description_relation:
                    rel_desc = cr.calculate_description_relation
                    rel_unit = cr.unit_measure_calculate
                if cr.analytical_method_calculate:
                    parts_rel.append(f"\\text{{{cr.analytical_method_calculate.calculate_description}}}")
                if cr.volumen_std:
                    parts_rel.append(str(cr.volumen_std))
                if cr.factor:
                    parts_rel.append(str(cr.factor))
                if cr.sample_quantity:
                    parts_rel.append(str(cr.sample_quantity))

                item_text_rel = " \cdot ".join(parts_rel)
                if not item_text_rel:
                    continue

                if cr.position == 'Numerador':
                    num_terms_rel.append(item_text_rel)
                elif cr.position == 'Denominador':
                    den_terms_rel.append(item_text_rel)
                elif cr.position == 'General':
                    gen_terms_rel.append(item_text_rel)

            str_num_rel = " \cdot ".join(num_terms_rel) if num_terms_rel else "1"
            str_den_rel = " \cdot ".join(den_terms_rel) if den_terms_rel else "1"
            str_gen_rel = f" \cdot {' \cdot '.join(gen_terms_rel)}" if gen_terms_rel else ""

            if rel_desc:
                label_rel = f"\\text{{{rel_desc}}}"
                if rel_unit:
                    label_rel += f" \\text{{ ({rel_unit})}}"
                context['final_equation_relation'] = f"{label_rel} = \\frac{{{str_num_rel}}}{{{str_den_rel}}}{str_gen_rel}"

        return context


# Vistas para Cálculos Dependientes de Productos
