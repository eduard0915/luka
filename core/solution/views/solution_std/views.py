import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView
from xhtml2pdf import pisa

from core.company.models import Company
from core.mixins import ValidatePermissionRequiredMixin
from core.reagent.models import InventoryReagent
from core.solution.forms import SolutionStandardForm
from core.solution.models import SolutionStd
from luka import settings


# Creación de Soluciones Estándar
class SolutionStandardCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = SolutionStd
    form_class = SolutionStandardForm
    template_name = 'solution_std/create_solution_std.html'
    permission_required = 'reagent.add_reagent'

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
                    self.object = form.save()
                    code_solution = form.cleaned_data.get('code_solution')
                    messages.success(request, f'Solución Estándar "{code_solution}" creada satisfactoriamente!')
                    # Provide redirect URL to detail view for AJAX to use
                    data['redirect_url'] = self.get_success_url()
                else:
                    messages.error(request, form.errors)
                    data['error'] = str(form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('solution:detail_solution_std', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparar Solución STD'
        context['action'] = 'add'
        context['entity'] = 'Preparar Solución Estándar'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        # Fallback cancel/back link to the solutions list
        try:
            context['list_url'] = reverse_lazy('solution:list_solution')
        except Exception:
            pass
        return context


# Listado de Soluciones
class SolutionStdListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = SolutionStd
    template_name = 'solution/list_solution.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                stds = list(SolutionStd.objects.select_related('solute_std__reagent', 'preparated_std_by').values(
                    'id',
                    'solute_std__reagent__description_reagent',
                    'code_solution_std',
                    'concentration_std',
                    'concentration_unit',
                    'preparation_std_date',
                    'expire_std_date_solution',
                    'quantity_solution_std',
                    'preparated_std_by__first_name',
                    'preparated_std_by__last_name',
                    'preparated_std_by__cargo',
                    'preparated_std_by',
                ).order_by('-code_solution_std'))

                # Formatear el nombre completo
                for std in stds:
                    first_name = std.get('preparated_std_by__first_name', '') or ''
                    last_name = std.get('preparated_std_by__last_name', '') or ''
                    cargo = std.get('preparated_std_by__cargo', '') or ''
                    std['preparated_std_by__get_full_name'] = f"{first_name} {last_name}, {cargo}".strip()

                return JsonResponse(stds, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Soluciones Estándar'
        context['create_url'] = reverse_lazy('solution:create_solution_std')
        context['entity'] = 'Soluciones Estándar'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['today'] = timezone.now()
        return context


# Detalle de Solución Estándar
class SolutionStdDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = SolutionStd
    template_name = 'solution_std/detail_solution_std.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparación de Solución Estándar'
        context['entity'] = 'Preparación de Solución Estándar'
        context['label_url'] = reverse_lazy('solution:solution_label_std_pdf', kwargs={'pk': self.object.pk})
        # if self.request.user.has_perm('user.add_user'):
        #     context['back'] = reverse_lazy('user:user_list')
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution_std')
        # context['update_solution'] = reverse_lazy('solution:update_solution', kwargs={'pk': self.object.pk})
        context['std'] = reverse_lazy('solution:create_solution_std', kwargs={'pk': self.object.pk})
        return context


@login_required
@require_http_methods(["GET"])
def get_inventory_reagent_data(request, reagent_id):
    """
    API endpoint para obtener datos de un reactivo del inventario
    """
    try:
        inventory_reagent = InventoryReagent.objects.select_related('reagent').get(id=reagent_id)

        data = {
            'id': str(inventory_reagent.id),
            'batch_number': inventory_reagent.batch_number,
            'purity': float(inventory_reagent.purity) if inventory_reagent.purity else None,
            'density': float(inventory_reagent.density) if inventory_reagent.density else None,
            'quantity_stock': float(inventory_reagent.quantity_stock) if inventory_reagent.quantity_stock else None,
            'date_expire': inventory_reagent.date_expire.isoformat() if inventory_reagent.date_expire else None,
            'reagent': {
                'id': str(inventory_reagent.reagent.id),
                'description': inventory_reagent.reagent.description_reagent,
                'code': inventory_reagent.reagent.code_reagent,
                'purity_unit': inventory_reagent.reagent.purity_unit,
                'molecular_weight': float(
                    inventory_reagent.reagent.molecular_weight) if inventory_reagent.reagent.molecular_weight else None,
                'gram_equivalent': float(
                    inventory_reagent.reagent.gram_equivalent) if inventory_reagent.reagent.gram_equivalent else None,
                'ready_to_use': inventory_reagent.reagent.ready_to_use,
                'stability_solution': inventory_reagent.reagent.stability_solution,
            }
        }
        return JsonResponse(data)
    except InventoryReagent.DoesNotExist:
        return JsonResponse({'error': 'Reactivo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Etiqueta de Identificación de Solución Estándar
class SolutionStdLabelPDFDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
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
        try:
            template = get_template('solution_std/label_solution_std.html')
            sln = SolutionStd.objects.get(pk=self.kwargs['pk'])
            company = Company.objects.first()

            context = {
                'sln': sln,
                'company': company,
                'title': f'Etiqueta Sln: {sln.code_solution_std}',
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

        except SolutionStd.DoesNotExist:
            messages.error(request, 'La solución Estándar no existe')
        except Exception as error:
            messages.error(request, f'Error al generar el PDF: {error}')
            print(f'Error al generar PDF: {error}')

        return HttpResponseRedirect(reverse_lazy('solution:list_solution_std'))
# class SolutionStdLabelPDFDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
#     permission_required = 'reagent.add_reagent'
#
#     @staticmethod
#     def link_callback(uri, rel):
#
#         # use short variable names
#         sUrl = settings.STATIC_URL  # Typically /static/
#         sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
#         mUrl = settings.MEDIA_URL  # Typically /static/media/
#
#         # convert URIs to absolute system paths
#         if uri.startswith(mUrl):
#             return uri
#         elif uri.startswith(sUrl):
#             path = os.path.join(sRoot, uri.replace(sUrl, ""))
#             if not os.path.isfile(path):
#                 raise Exception(
#                     'Logo provided do not exists on path given: %s' % path
#                 )
#             return path
#         return None
#
#     def get(self, request, *args, **kwargs):
#         try:
#             template = get_template('solution_std/label_solution_std.html')
#             std = SolutionStd.objects.get(pk=self.kwargs['pk'])
#             context = {
#                 'std': SolutionStd.objects.get(pk=self.kwargs['pk']),
#                 'company': Company.objects.first(),
#                 'title': 'Etiqueta STD: ' + std.code_solution_std,
#                 'page_size': '101.6mm 80.8mm',
#             }
#             html = template.render(context)
#             response = HttpResponse(content_type='application/pdf')
#             pisa.CreatePDF(
#                 html, dest=response,
#                 link_callback=self.link_callback
#             )
#             return response
#         except ValueError as error:
#             print(f'Tiene un valor errado: {error}')
#         except TypeError as error:
#             print(f'Tiene un error de tipo: {error}')
#             pass
#         return HttpResponseRedirect(reverse_lazy('solution:list_solution_std'))
