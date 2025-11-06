import os
from urllib.request import urlopen

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from decouple import config
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
from core.solution.models import Solution
from luka import settings


# Creación de Soluciones
class SolutionCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'create_three.html'
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
                    messages.success(request, f'Solución "{code_solution}" creada satisfactoriamente!')
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
        return reverse('solution:detail_solution', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparar Solución'
        context['action'] = 'add'
        context['entity'] = 'Preparar Solución'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        # Fallback cancel/back link to the solutions list
        try:
            context['list_url'] = reverse_lazy('solution:list_solution')
        except Exception:
            pass
        return context


# Listado de Soluciones
class SolutionListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Solution
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
                reagents = list(Solution.objects.select_related('solute_reagent__reagent', 'preparated_by').values(
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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Soluciones'
        context['create_url'] = reverse_lazy('solution:create_solution')
        context['create_url_std'] = reverse_lazy('solution:create_solution_std')
        context['entity'] = 'Soluciones'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['today'] = timezone.now()
        return context


# Edición de Soluciones
class SolutionUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'solution/update_solution.html'
    permission_required = 'reagent.change_reagent'

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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Solución a Preparar'
        context['entity'] = 'Editar Solución a Preparar'
        context['action'] = 'edit'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:detail_solution', kwargs={'pk': self.object.pk})
        return context


# Adición de Solvente
class SolutionAddSolventUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Solution
    form_class = SolutionAddSolventForm
    template_name = 'solution/create_solvent.html'
    permission_required = 'reagent.add_reagent'

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
                    messages.success(request, f'Solvente Añadido satisfactoriamente!')
                else:
                    messages.error(request, form.errors)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Adición de Solvente'
        context['action'] = 'edit'
        context['class'] = 'col-md-6'
        context['info_form'] = self.object.solvent_reagent.reagent.description_reagent + ' al ' + str(self.object.solvent_reagent.purity) + self.object.solvent_reagent.reagent.purity_unit
        return context


# Detalle de Soluciones
class SolutionDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DetailView):
    model = Solution
    template_name = 'solution/detail_solution.html'
    permission_required = 'reagent.add_reagent'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Preparación de Solución'
        context['entity'] = 'Preparación de Solución'
        context['label_url'] = reverse_lazy('solution:solution_label_pdf', kwargs={'pk': self.object.pk})
        # if self.request.user.has_perm('user.add_user'):
        #     context['back'] = reverse_lazy('user:user_list')
        context['icon'] = 'fa-solid fa-flask-vial'
        context['list_url'] = reverse_lazy('solution:list_solution')
        context['update_solution'] = reverse_lazy('solution:update_solution', kwargs={'pk': self.object.pk})
        context['std'] = reverse_lazy('solution:create_solution_std', kwargs={'pk': self.object.pk})
        return context


# Etiqueta de Identificación de Solución
class SolutionLabelPDFDetailView(LoginRequiredMixin, ValidatePermissionRequiredMixin, View):
    permission_required = 'reagent.add_reagent'

    @staticmethod
    def link_callback(uri, rel):

        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            return uri
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
            if not os.path.isfile(path):
                raise Exception(
                    'Logo provided do not exists on path given: %s' % path
                )
            return path

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('solution/label_solution.html')
            sln = Solution.objects.get(pk=self.kwargs['pk'])
            context = {
                'sln': Solution.objects.get(pk=self.kwargs['pk']),
                'company': Company.objects.first(),
                'title': 'Etiqueta Sln: ' + sln.code_solution,
                # 'page_size': '101.6mm 101.6mm',
                'page_size': '101.6mm 50.8mm',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            return response
        except ValueError as error:
            print(f'Tiene un valor errado: {error}')
        except TypeError as error:
            print(f'Tiene un error de tipo: {error}')
            pass
        return HttpResponseRedirect(reverse_lazy('solution:list_solution'))
