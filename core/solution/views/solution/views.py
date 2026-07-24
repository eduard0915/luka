import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from xhtml2pdf import pisa

from core.company.models import Company
from core.mixins import ValidatePermissionRequiredMixin
from core.solution.forms import *
from core.solution.models import Solution, StandardizationSolution, TransactionSolution
from luka import settings


"""Vistas CRUD para la gestión de soluciones del laboratorio."""
class SolutionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    """Vista para la creación de una nueva solución en el laboratorio."""
    model = Solution
    form_class = SolutionForm
    template_name = 'solution/create_solution.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Inicializa el objeto como nulo y maneja la petición."""
        self.object = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de creación de solución vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code_solution = form.cleaned_data.get('code_solution')
                    messages.success(request, f'Solución "{code_solution}" creada satisfactoriamente!')
                    # Provide redirect URL to detail view for AJAX to use
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            error_messages.extend([str(e) for e in errors])
                        else:
                            field_label = form.fields[field].label or field
                            for error in errors:
                                error_messages.append(f"{field_label}: {error}")

                    error_text = '<br>'.join(error_messages)
                    messages.error(request, error_text)
                    data['error'] = error_text
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        """Retorna la URL de detalle de la solución creada."""
        return reverse('solution:detail_solution', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        """Agrega título, acción y URLs al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparar Solución'
        context['action'] = 'add'
        context['entity'] = 'Preparar Solución'
        context['div'] = '11'
        context['icon'] = 'fa-solid fa-flask-vial'
        # Fallback cancel/back link to the solutions list
        try:
            context['list_url'] = reverse_lazy('solution:list_solution')
        except Exception:
            context['list_url'] = reverse_lazy('solution:list_solution')
        return context


@login_required
@require_http_methods(["GET"])
def get_solution_base_data(request, base_id):
    """
    API endpoint para obtener datos de una Solución Base o Solución Estándar Base
    """
    try:
        # Intentar buscar en SolutionBase
        base = SolutionBase.objects.filter(id=base_id).first()
        if base:
            data = {
                'id': str(base.id),
                'solute_reagent_id': str(base.solute_reagent_base.id),
                'solvent_reagent_id': str(base.solvent_reagent_base.id) if base.solvent_reagent_base else None,
                'concentration': base.concentration_base,
                'concentration_unit': base.concentration_unit_base,
            }
            return JsonResponse(data)
        
        # Si no se encuentra, intentar buscar en SolutionStdBase
        base_std = SolutionStdBase.objects.filter(id=base_id).first()
        if base_std:
            data = {
                'id': str(base_std.id),
                'solute_reagent_id': str(base_std.solute_std_base.id),
                'solvent_reagent_id': str(base_std.solvent_reagent_base.id) if base_std.solvent_reagent_base else None,
                'concentration': base_std.concentration_std_base,
                'concentration_unit': base_std.concentration_unit_base,
            }
            return JsonResponse(data)

        return JsonResponse({'error': 'Solución Base no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Listado de Soluciones
class SolutionListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    """Vista para listar todas las soluciones registradas."""
    model = Solution
    template_name = 'solution/list_solution.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición del listado de soluciones."""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la solicitud AJAX de búsqueda y retorna datos JSON."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                reagents = list(Solution.objects.values(
                    'id',
                    'solute_reagent__reagent__description_reagent',
                    'code_solution',
                    'concentration',
                    'concentration_unit',
                    'preparation_date',
                    'expire_date_solution',
                    'quantity_solution',
                    'preparated_by__first_name',
                    'preparated_by__last_name',
                    'preparated_by__cargo',
                    'preparated_by',
                    'quantity_solvent',
                    'preparation_confirmed',
                    'quantity_available_sln'
                ).order_by('-code_solution'))

                # Formatear el nombre completo
                for reagent in reagents:
                    first_name = reagent.get('preparated_by__first_name', '') or ''
                    last_name = reagent.get('preparated_by__last_name', '') or ''
                    cargo = reagent.get('preparated_by__cargo', '') or ''
                    reagent['preparated_by__get_full_name'] = f"{first_name} {last_name}, {cargo}".strip()

                return JsonResponse(reagents, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        """Agrega título, URL de creación y entidad al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Soluciones'
        context['create_url'] = reverse_lazy('solution:create_solution')
        context['entity'] = 'Soluciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['today'] = timezone.localdate()
        return context


# Edición de Soluciones
class SolutionUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para editar una solución existente."""
    model = Solution
    form_class = SolutionForm
    template_name = 'solution/update_solution.html'
    permission_required = 'reagent.change_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene la solución a editar y maneja la petición."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa el formulario de edición de solución."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    self.object = form.save()
                    code_solution = form.cleaned_data.get('code_solution')
                    messages.success(request, f'Solución "{code_solution}" editada satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
                return redirect(self.get_context_data()['list_url'])
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega título, acción y URLs al contexto de edición."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Solución a Preparar'
        context['entity'] = 'Editar Solución a Preparar'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:detail_solution', kwargs={'pk': self.object.pk})
        return context


# Confirmación de Preparación de solución
class SolutionConfirmedUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    """Vista para confirmar la preparación de una solución."""
    model = Solution
    form_class = SolutionConfirmedForm
    template_name = 'solution/confirmed_solution.html'
    permission_required = 'reagent.add_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Obtiene la solución a confirmar."""
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Procesa la confirmación de preparación vía AJAX."""
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Solvente Añadido satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """Agrega entidad e información de confirmación al contexto."""
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Preparación de Solución ' + self.object.code_solution
        context['action'] = 'edit'
        context['class'] = 'col-md-6'
        context['info_form'] = 'Confirma Preparación? Después de Confirmada No podrá editarse'
        return context


# Detalle de Soluciones
class SolutionDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    """Vista de detalle de una solución con transacciones y estandarizaciones."""
    model = Solution
    template_name = 'solution/detail_solution.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        """Maneja la petición de detalle de la solución."""
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega transacciones, estandarizaciones y URLs al contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparación de Solución'
        context['entity'] = 'Preparación de Solución'
        context['label_url'] = reverse_lazy('solution:solution_label_pdf', kwargs={'pk': self.object.pk})
        # if self.request.user.has_perm('user.add_user'):
        #     context['back'] = reverse_lazy('user:user_list')
        context['std_config'] = Standardization.objects.filter(solution_reagent_id=self.object.solute_reagent.reagent.id).first()
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution')
        context['standardizations'] = StandardizationSolution.objects.select_related('solution').filter(solution_id=self.object.id)
        context['standard_count'] = StandardizationSolution.objects.select_related('solution').filter(solution_id=self.object.id).count()
        context['transactions'] = TransactionSolution.objects.select_related('solution_inventory').filter(solution_inventory_id=self.object.id)
        context['update_solution'] = reverse_lazy('solution:update_solution', kwargs={'pk': self.object.pk})
        context['add_standardization'] = reverse_lazy('solution:create_std_solution', kwargs={'pk': self.object.pk})
        return context


# Etiqueta de Identificación de Solución
class SolutionLabelPDFDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    """Vista para generar la etiqueta PDF de identificación de una solución."""
    permission_required = 'reagent.add_reagent'

    @staticmethod
    def link_callback(uri, rel):
        """
        Convierte URIs a rutas absolutas del sistema de archivos
        """
        sUrl = settings.STATIC_URL  # Típicamente /static/
        sRoot = settings.STATIC_ROOT  # Típicamente /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Típicamente /media/
        mRoot = settings.MEDIA_ROOT  # Típicamente /home/userX/project_media/

        # Convertir URIs a rutas absolutas del sistema
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        # Verificar que el archivo existe
        if not os.path.isfile(path):
            print(f'Advertencia: El archivo no existe en la ruta: {path}')
            return None

        return path

    def get(self, request, *args, **kwargs):
        """Genera y retorna el PDF de la etiqueta de identificación."""
        try:
            template = get_template('solution/label_solution.html')
            sln = Solution.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'sln': sln,
                'company': company,
                'title': f'Etiqueta Sln: {sln.code_solution}',
                'page_size': '101.6mm 80.8mm',
            }

            # Si existe logo, agregar la ruta ABSOLUTA del sistema
            if company and company.company_logo:
                logo_path = os.path.join(settings.MEDIA_ROOT, str(company.company_logo))
                if os.path.isfile(logo_path):
                    context['company_logo_path'] = logo_path
                else:
                    print(f'Advertencia: Logo no encontrado en: {logo_path}')

            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')

            pisa_status = pisa.CreatePDF(
                html,
                dest=response,
                link_callback=self.link_callback
            )

            if pisa_status.err:
                raise Exception('Error al generar el PDF')

            return response

        except Solution.DoesNotExist:
            messages.error(request, 'La solución no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')
            print(f'Error al generar PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('solution:list_solution'))
