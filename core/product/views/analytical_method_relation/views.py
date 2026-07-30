
"""Vistas para la gestión de relaciones de cálculo dependientes de productos.

Incluye la creación, edición y eliminación de descripciones de cálculo,
relaciones de cálculo, volumen estándar, factor constante y cantidad de muestra.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.mixins import ValidatePermissionRequiredMixin
from core.product.forms import (
    ProductCalculateRelationDescriptionForm, ProductCalculateRelationForm,
    ProductVolumenStdRelationForm, ProductFactorRelationForm, ProductSampleGramRelationForm,
    ProductCalculateRelationAddForm
)
from core.product.models import Product
from core.analytical_method.models import AnalyticalMethodCalculateRelation, DependentCalculation


class BaseProductCalculateRelationView(ValidatePermissionRequiredMixin):
    """Vista base con permisos y lógica compartida para las relaciones de cálculo de productos."""

    permission_required = 'reagent.add_reagent'
    template_name = 'modal_one.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Procesa la petición HTTP con protección CSRF desactivada."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa las acciones de agregar, editar o eliminar una relación de cálculo vía AJAX."""
        data = {}
        try:
            action = request.POST.get('action')
            if action == 'add':
                product = Product.objects.get(pk=self.kwargs.get('pk'))
                dependent_calculation = DependentCalculation.objects.get(pk=self.kwargs.get('dep_pk'))
                form = self.get_form_class()(
                    request.POST, product=product, dependent_calculation=dependent_calculation)
            elif action == 'edit':
                self.object = self.get_object()
                form = self.get_form()
            elif action == 'delete':
                self.object = self.get_object()
                self.object.delete()
                messages.success(request, f'Operación realizada con éxito!')
                return JsonResponse(data)
            else:
                data['error'] = 'No ha ingresado una acción válida'
                return JsonResponse(data)

            if form.is_valid():
                form.save()
                messages.success(request, f'Operación realizada con éxito!')
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega la clase CSS para el ancho del modal al contexto."""
        context = super().get_context_data(**kwargs)
        context['class'] = 'col-lg-12'
        return context


class ProductCalculateRelationDescriptionCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para crear una descripción de cálculo relacional para un producto."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationDescriptionForm

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Descripción de Cálculo'
        context['action'] = 'add'
        return context


class ProductCalculateRelationDescriptionUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar una descripción de cálculo relacional de un producto."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationDescriptionForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Descripción de Cálculo'
        context['action'] = 'edit'
        return context


class ProductCalculateRelationCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para crear una relación de cálculo con un método analítico."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationForm

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo Relacionado'
        context['action'] = 'add'
        return context


class ProductCalculateRelationUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar una relación de cálculo de un producto."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo Relacionado'
        context['action'] = 'edit'
        return context


class ProductCalculateRelationAddCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para relacionar un cálculo registrado en un consecutivo anterior."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationAddForm

    def get_form_kwargs(self):
        """Inyecta el producto y el cálculo dependiente actual en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        dependent_calculation = DependentCalculation.objects.get(pk=self.kwargs.get('dep_pk'))
        kwargs.update({'product': product, 'dependent_calculation': dependent_calculation})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cálculo Relacionado Add'
        context['action'] = 'add'
        return context


class ProductCalculateRelationAddUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar la relación con un cálculo de un consecutivo anterior."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductCalculateRelationAddForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cálculo Relacionado Add'
        context['action'] = 'edit'
        return context


class ProductVolumenStdRelationCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para crear una relación de volumen estándar en un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductVolumenStdRelationForm

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Volumen Estándar'
        context['action'] = 'add'
        return context


class ProductVolumenStdRelationUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar una relación de volumen estándar de un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductVolumenStdRelationForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Volumen Estándar'
        context['action'] = 'edit'
        return context


class ProductFactorRelationCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para crear una relación de factor constante en un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductFactorRelationForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Constante'
        context['action'] = 'add'
        return context


class ProductFactorRelationUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar una relación de factor constante de un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductFactorRelationForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Constante'
        context['action'] = 'edit'
        return context


class ProductSampleGramRelationCreateView(LoginRequiredMixin, BaseProductCalculateRelationView, CreateView):
    """Vista para crear una relación de cantidad de muestra en un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductSampleGramRelationForm

    def get_form_kwargs(self):
        """Inyecta el producto actual en los kwargs del formulario."""
        kwargs = super().get_form_kwargs()
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        kwargs.update({'product': product})
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Agregar Cantidad de Muestra'
        context['action'] = 'add'
        return context


class ProductSampleGramRelationUpdateView(LoginRequiredMixin, BaseProductCalculateRelationView, UpdateView):
    """Vista para editar una relación de cantidad de muestra de un cálculo."""

    model = AnalyticalMethodCalculateRelation
    form_class = ProductSampleGramRelationForm

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Editar Cantidad de Muestra'
        context['action'] = 'edit'
        return context


class ProductCalculateRelationDeleteView(LoginRequiredMixin, BaseProductCalculateRelationView, DeleteView):
    """Vista para eliminar una relación de cálculo de un producto."""

    model = AnalyticalMethodCalculateRelation
    template_name = 'delete_modal.html'

    def get_context_data(self, **kwargs):
        """Agrega el título y la acción al contexto del modal de eliminación."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Eliminar Cálculo'
        context['action'] = 'delete'
        return context
