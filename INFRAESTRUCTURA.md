# Infraestructura del Proyecto Luka LIMS

Documentación de referencia para replicar la arquitectura e infraestructura en otros proyectos Django.

---

## 1. Estructura General del Proyecto

```
luka/                    # Configuración del proyecto (settings, urls, wsgi)
core/                    # Todas las apps de dominio
  analytical_method/     # Métodos analíticos y cálculos
  company/               # Empresas, sitios, procesos
  condition/             # Condiciones ambientales
  equipment/             # Equipos, calibraciones, mantenimiento
  home/                  # Landing page
  laboratory/            # Laboratorios
  login/                 # Autenticación
  observation/           # Observaciones
  product/               # Productos, especificaciones, puntos de muestreo
  reagent/               # Reactivos
  report/                # Reportes
  sampling/              # Muestreos, muestras, análisis
  solution/              # Soluciones estándar
  user/                  # Usuarios y capacitaciones
  mixins.py              # ValidatePermissionRequiredMixin
  models.py              # BaseModel (abstracto)
  utils.py               # format_form_errors()
  validators.py          # Validadores de archivos
  context_processors.py  # extras_processor (global)
templates/               # Plantillas base (HTML, modales, layouts CRUD)
  base.html              # Raíz: HTML skeleton, CSS, JS de cabecera
  body.html              # Layout principal: header, sidebar, footer, main
  create_one.html        # Formulario simple (1 columna) con axios
  create_two.html        # Formulario multi-columna con axios + SweetAlert2
  create_three.html      # Como create_two con datepicker + solution_filter.js
  list_one.html          # DataTable scaffold
  detail_one.html        # Placeholder para vistas de detalle
  modal_one.html         # Modal con {{ form.as_p }} + datepicker
  modal_two.html         # Modal con iteración manual de campos
  modal_three.html       # Modal con col_class grid + SweetAlert2
  modal_four.html        # Modal-lg con confirm_msg + validaciones
  delete_modal.html      # Modal de eliminación con spinner
  header.html            # Navbar: logo, notificaciones, menú usuario
  sidebar.html           # Menú lateral treeview con path_helpers
  footer.html            # Footer (comentado)
static/                  # CSS, JS, imágenes, vendor libs
templatetags/            # custom_filters, path_helpers
docs/
```

---

## 2. Sistema de Herencia de Templates

### Jerarquía

```
base.html
  └── body.html
        ├── create_one.html    (formularios simples)
        ├── create_two.html    (formularios multi-columna)
        ├── create_three.html  (formularios con datepicker avanzado)
        ├── list_one.html      (listados con DataTables)
        └── detail_one.html    (vista de detalle)
```

Los modales **no extienden** de `base.html` — son fragmentos HTML autónomos cargados vía `open_modal(url)` en un `<div id="modal_template">`.

### `base.html` — Esqueleto raíz

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <title>{{ title }}</title>
    <!-- CSS: vali-admin main.css, my_styles.css, timepicker.css -->
    <!-- Bootstrap Icons, FontAwesome 7.1.0 -->
    <!-- Vanilla JS Datepicker CSS -->
    <!-- JS en head: Datepicker full, axios, SweetAlert2 -->
    <!-- Select2 CSS + BS5 theme -->
    {% block head %}{% endblock %}
</head>
{% block body %}{% endblock %}
</html>
```

**Variables de contexto requeridas**: `{{ title }}`

### `body.html` — Layout principal

```html
{% extends 'base.html' %}

{% block body %}
<body class="app sidebar-mini">
    {% include 'header.html' %}
    {% include 'sidebar.html' %}

    <main class="app-content">
        <!-- Título y breadcrumb -->
        <div class="app-title">
            <h1><i class="{{ icon }}"></i> {{ entity }}</h1>
            <p>{{ subentity }}</p>
            {% block buttons %}{% endblock %}
        </div>

        <!-- Notificaciones Django messages -->
        {% block notifications %}
            <!-- alertas con Bootstrap: success/danger/warning -->
        {% endblock %}

        <!-- Contenido de la página -->
        {% block content %}{% endblock %}

        <!-- Contenedor de modales -->
        <div class="modal" id="modal_template"></div>
    </main>

    <!-- JS al final: jQuery, Bootstrap, main.js, Select2 -->
    <script>
        function open_modal(url) {
            $('#modal_template').load(url, function () {
                $(this).modal('show');
            });
        }
    </script>
    {% block form_javascript %}{% endblock %}
    {% block scripts_detail %}{% endblock %}
</body>
{% endblock %}
```

**Variables de contexto requeridas**: `{{ icon }}`, `{{ entity }}`, `{{ subentity }}`, `{{ back }}`

### `header.html` — Barra de navegación

- Logo con enlace a `{% url 'start:start' %}`
- Botón toggle sidebar
- Nombre del laboratorio del usuario
- Campana de notificaciones con badge `{{ count_total_alarm }}`:
  - Capacitaciones vencidas
  - Mantenimientos vencidos
  - Calibraciones vencidas
- Dropdown de usuario: Mi Perfil, Resetear Contraseña, Logout

### `sidebar.html` — Menú lateral

Usa `{% load path_helpers %}` (cargado como built-in en settings) para controlar estados activos/expandidos:

```html
<!-- Ejemplo de item con submenú -->
<li class="{% is_expanded 'sampling/' 'analysis/' as expanded %}">
    <a class="{% is_active_section 'sampling/' 'analysis/' %}">
        <i class="fa-solid fa-flask"></i> Análisis Químico
    </a>
    <ul class="treeview-menu {% if expanded %}is-expanded{% endif %}">
        <li><a class="{% is_active_section 'analytical_method/' %}"
               href="{% url 'analytical_method:list_analytical_method' %}">Métodos</a></li>
        <!-- más items... -->
    </ul>
</li>
```

Los permisos se verifican con `{% if perms.app_label.action_model %}`.

### Layouts de formulario

#### `create_one.html` — Formulario simple (1 columna)

Itera `form.visible_fields`, cada uno en `.mb-3`. Submit vía **axios** con spinner:

```javascript
document.getElementById('mainForm').addEventListener('submit', function (e) {
    e.preventDefault();
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando...';
    const parameters = new FormData(this);
    axios.post(window.location.pathname, parameters, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }).then(function (response) {
        if (!response.data.hasOwnProperty('error')) {
            location.href = '{{ list_url }}';
        }
        message_error(response.data.error);
        btnSubmit.disabled = false;
    });
});
```

#### `create_two.html` — Formulario multi-columna

Usa `field.field.col_class` para definir ancho de cada campo (default `col-md-3`). Submit vía axios con **SweetAlert2** para éxito/error:

```javascript
axios.post(window.location.pathname, parameters, { ... })
    .then(function (response) {
        if (response.data.success) {
            Swal.fire({ icon: 'success', title: '¡Éxito!',
                text: 'Operación realizada satisfactoriamente',
                timer: 2000, showConfirmButton: false
            }).then(() => { location.href = response.data.redirect_url; });
            return;
        }
        if (response.data.error) {
            Swal.fire({ icon: 'error', title: 'Error de Validación',
                html: response.data.error });
        }
    });
```

Carga condicional de JS específicos según `{{ entity }}`:
- `form_inventory_reagent.js`
- `form_sampling_group.js`
- `form_sampling_process.js`
- `form_daily_verification.js`
- `datetime.js` (siempre cargado para datepickers)

#### `create_three.html` — Similar a create_two, con:
- Datepicker inicializado inline (wraps inputs en input-group con botón calendario)
- `solution_filter.js` condicional

### Variables de contexto para formularios

| Variable     | Uso                                              |
|--------------|--------------------------------------------------|
| `{{ title }}` | Título de la página (tag `<title>`)             |
| `{{ entity }}` | Título en el app-title y modales               |
| `{{ subtitle }}` | Subtítulo dentro del tile                     |
| `{{ action }}` | `'add'` o `'edit'` — enviado como hidden input |
| `{{ div }}` | Ancho Bootstrap (`'8'`, `'10'`, `'12'`)        |
| `{{ icon }}` | Clase FontAwesome (`'fa-solid fa-flask'`)       |
| `{{ list_url }}` | URL para botón Cancelar y redirección        |

---

## 3. Sistema de Modales

### Carga dinámica

En `body.html` existe `<div class="modal" id="modal_template">`. Los modales se cargan con:

```javascript
function open_modal(url) {
    $('#modal_template').load(url, function () {
        $(this).modal('show');
    });
}
```

En las vistas, un botón llama a `open_modal()` con la URL del endpoint que retorna el modal:

```html
<button onclick="open_modal('{% url 'app:create_xxx' %}')" class="btn btn-primary">
    Nuevo
</button>
```

### Tipos de modal

| Archivo           | Tamaño      | Renderizado de campos          | Submit     | Notificaciones | Extras                    |
|-------------------|-------------|-------------------------------|------------|----------------|---------------------------|
| `modal_one.html`  | Default     | `{{ form.as_p }}`             | jQuery AJAX| `message_error()`| Datepicker auto-init |
| `modal_two.html`  | Default     | Loop `form.visible_fields`    | jQuery AJAX| `message_error()`| `detail_button` opcional |
| `modal_three.html`| Default     | Loop con `field.col_class`    | jQuery AJAX| SweetAlert2     | Datepicker + JS condicional |
| `modal_four.html` | `modal-lg`  | Loop con `field.col_class`    | jQuery AJAX| `message_error()`| `confirm_msg`, `detail_button` |
| `delete_modal.html`| Default    | Sin campos (solo `object.id`) | jQuery AJAX| Recarga página | Spinner "Eliminando..." |

### Convenciones de los modales

- Cada modal es un `<div>` autocontenido (no extiende de base.html)
- `action` se envía como `<input type="hidden" name="action" value="{{ action }}">`
- Acciones comunes: `'add'`, `'edit'`, `'delete'`
- `action_url` puede ser personalizado: `{{ action_url|default:request.path }}`
- Envío vía jQuery AJAX con `FormData` (soporta archivos)
- En éxito: redirige a `data.redirect_url` o recarga `window.location.pathname`
- En error: muestra `data.error`

---

## 4. Listados con DataTables

### Setup en `list_one.html`

```html
{% extends 'body.html' %}

{% block content %}
<div class="row">
    <div class="col-md-{{ div }}">
        <div class="tile">
            <div class="tile-body">
                <div class="table-responsive">
                    <table class="table table-hover table-bordered" id="data">
                        <thead>
                        {% block columns %}{% endblock %}
                        </thead>
                        <tbody>
                        {% block rows %}{% endblock %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts_detail %}
    <script src="{% static 'lib/vali-admin/js/plugins/jquery.dataTables.min.js' %}"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/v/bs5/dt-1.13.4/datatables.min.css">
{% endblock %}
```

### Inicialización de DataTable (ejemplo real)

Se hace en el template específico que extiende `list_one.html`, dentro de `{% block scripts_detail %}`:

```javascript
// Template: process_sampling/list_process_sampling.html
{% block scripts_detail %}
    {{ block.super }}
    <script src="{% static 'sampling/list_process_sampling.js' %}"></script>
{% endblock %}
```

El JS externo (`list_process_sampling.js`):

```javascript
$(function () {
    $('#data').DataTable({
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata',
                'status_filter': 'Programada',
            },
            dataSrc: ""
        },
        columns: [
            {"data": "number_sample"},
            {"data": "date_sampling"},
            // ... más columnas
        ],
        columnDefs: [
            {
                targets: [-1],  // columna de acciones
                render: function (data, type, row) {
                    return `
                        <a href="/sampling/process/detail/${row.id}/" class="btn btn-info btn-sm">
                            <i class="fa-solid fa-circle-info"></i>
                        </a>
                        <a href="/sampling/process/update/${row.id}/" class="btn btn-warning btn-sm">
                            <i class="fa-solid fa-pencil"></i>
                        </a>`;
                }
            },
        ],
        language: { url: '//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json' },
    });
});
```

### Patrón del endpoint AJAX

La vista que sirve el listado es un `ListView` con `csrf_exempt` que responde a POST con `action == 'searchdata'`:

```python
class LaboratoryListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                results = list(Model.objects.select_related('fk')
                    .values('id', 'field1', 'fk__name')
                    .order_by('field1'))
                # Formatear valores para display si es necesario
                for item in results:
                    item['bool_display'] = 'Sí' if item.get('bool_field') else 'No'
                return JsonResponse(results, safe=False)
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
```

**Importante**: `select_related()` para FKs, `values()` para datos planos, `safe=False` en el `JsonResponse` porque se envía una lista (no un dict).

### Subclases de ListView para filtros

Se crean subclases con atributos adicionales de filtro:

```python
class SamplingProcessScheduledListView(SamplingProcessListView):
    extra_context = {'title': 'Muestreos Programados'}
    status_filter = 'Programada'
```

---

## 5. Vistas CRUD (Create, Read, Update, Delete)

Todas las vistas siguen el mismo patrón estricto.

### CreateView

```python
from core.mixins import ValidatePermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

class LaboratoryCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Laboratory
    form_class = LaboratoryForm
    template_name = 'lab/create_laboratory.html'
    permission_required = 'laboratory.add_laboratory'  # app_label.action_modelname

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
                    messages.success(request, 'Creado satisfactoriamente!')
                    data['success'] = True
                    data['redirect_url'] = self.get_success_url()
                else:
                    error_text = format_form_errors(form)  # usarla en vez de inline
                    messages.error(request, error_text)
                    data['error'] = error_text
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_success_url(self):
        return reverse('laboratory:list_laboratory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Laboratorio'
        context['action'] = 'add'
        context['entity'] = 'Laboratorios'
        context['div'] = '8'
        context['icon'] = 'fa-solid fa-flask'
        context['list_url'] = reverse_lazy('laboratory:list_laboratory')
        return context
```

### UpdateView — Igual estructura, cambia:

- `action == 'edit'` en el POST
- `self.object = self.get_object()` en dispatch
- Mensaje: "editado satisfactoriamente"

### DeleteView — Simplificado

Se maneja frecuentemente desde el modal `delete_modal.html` usando el mismo `ListView` o una vista específica. El POST contiene `action='delete'` y `id=object.id`. La vista busca el objeto, lo elimina y retorna `JsonResponse({})`.

```python
def post(self, request, *args, **kwargs):
    data = {}
    try:
        action = request.POST['action']
        if action == 'delete':
            obj = self.model.objects.get(pk=request.POST['id'])
            obj.delete()
        else:
            data['error'] = 'Acción no válida'
    except Exception as e:
        data['error'] = str(e)
    return JsonResponse(data)
```

### DetailView — Datos adicionales con DataTables

A menudo se usan múltiples DataTables en la misma página de detalle, con IDs `#data_0`, `#data_1`, etc.

### Nombres de URL

```
app_name = 'laboratory'

urlpatterns = [
    path('add/', CreateView.as_view(), name='create_model'),
    path('list/', ListView.as_view(), name='list_model'),
    path('update/<uuid:pk>/', UpdateView.as_view(), name='update_model'),
    path('detail/<uuid:pk>/', DetailView.as_view(), name='detail_model'),
    path('delete/<uuid:pk>/', DeleteView.as_view(), name='delete_model'),
]
```

---

## 6. Carpeta `views/` — Organización por sub-recurso

En apps complejas, las vistas se organizan en subdirectorios:

```
core/sampling/views/
  __init__.py
  group_sampling/
    __init__.py
    views.py        # SamplingGroupCreateView, ListView, UpdateView, etc.
  process_sampling/
    __init__.py
    views.py        # SamplingProcessCreateView, ListView, DetailView, etc.
  analysis_sampling/
    views.py        # SamplingAnalysisDetailView, procesamiento, etc.
  massive_analysis_sampling/
    views.py        # Cargue masivo de análisis
```

Las importaciones en `urls.py` usan wildcard:

```python
from core.sampling.views.group_sampling.views import *
from core.sampling.views.process_sampling.views import *
```

---

## 7. Patrón de Formularios

### Estructura base

```python
from crum import get_current_user
from django.forms import ModelForm, TextInput, Select

class MiModeloForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = get_current_user()
        # Filtrar querysets según el laboratorio/sitio del usuario
        if user.laboratory:
            self.fields['campo_fk'].queryset = ModeloRelacionado.objects.filter(
                enable=True, site=user.laboratory.site)
        else:
            self.fields['campo_fk'].queryset = ModeloRelacionado.objects.none()

        # Deshabilitar autocomplete
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        # Definir clases de columna Bootstrap para el grid del formulario
        col_classes = {
            'codigo': 'col-md-2',
            'nombre': 'col-md-4',
            'descripcion': 'col-md-6',
        }
        for field_name, field in self.fields.items():
            field.col_class = col_classes.get(field_name, 'col-md-3')

    class Meta:
        model = MiModelo
        fields = ['codigo', 'nombre', 'descripcion', 'campo_fk']
        widgets = {
            'codigo': TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'nombre': TextInput(attrs={'class': 'form-control', 'required': True}),
            'campo_fk': Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        }
```

### Convenciones clave

1. **`col_class`** en cada field: se asigna en `__init__` como atributo dinámico, se usa en `create_two.html` / `create_three.html` / `modal_three.html` / `modal_four.html`:
   ```html
   <div class="{% if field.field.col_class %}{{ field.field.col_class }}{% else %}col-md-3{% endif %}">
   ```

2. **`get_current_user()`** de `django-crum`: se usa en `__init__` para filtrar querysets según el laboratorio/sitio del usuario autenticado.

3. **Select2**: se usa la clase CSS `select2` en widgets Select; Select2 se inicializa en `body.html`:
   ```javascript
   $('.select2').each(function() {
       $(this).select2({ theme: 'bootstrap-5', width: '100%', language: 'es' });
   });
   ```

4. **Validaciones en `clean()`**: lógica de negocio y cálculos van en `clean()`. Los valores calculados se guardan en `cleaned_data` con prefijo `_` (ej: `cleaned_data['_quantity_reagent']`) y se consumen en `save()`.

5. **Formularios separados para create vs update**: se crea `MiModeloUpdateForm` que hereda de `ModelForm` con querysets que incluyen el valor actual del objeto (usando `|` para unir al queryset filtrado):
   ```python
   if self.instance and self.instance.pk and self.instance.related_id:
       qs = qs | ModeloRelacionado.objects.filter(pk=self.instance.related_id)
   self.fields['campo_fk'].queryset = qs
   ```

6. **Forms que retornan dict en save()**: algunos formularios de configuración retornan `{'error': ...}` en lugar de lanzar excepción:
   ```python
   def save(self, commit=True):
       data = {}
       try:
           if form.is_valid():
               data = form.save()
           else:
               data['error'] = form.errors
       except Exception as e:
           data['error'] = str(e)
       return data
   ```

---

## 8. `core/mixins.py` — ValidatePermissionRequiredMixin

```python
from django.shortcuts import redirect
from django.urls import reverse_lazy

class ValidatePermissionRequiredMixin(object):
    permission_required = ''
    url_redirect = None

    def get_perms(self):
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('start:notperms')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_perms(self.get_perms()):
            return super().dispatch(request, *args, **kwargs)
        return redirect(self.get_url_redirect())
```

**Uso en todas las vistas**: `LoginRequiredMixin` + `ValidatePermissionRequiredMixin` como primeras clases base. El permiso sigue el formato `'app_label.action_modelname'` (ej: `'sampling.view_samplingprocess'`).

---

## 9. `core/models.py` — BaseModel

```python
from django.conf import settings
from django.db import models

class BaseModel(models.Model):
    """Modelo abstracto con campos de auditoría para todas las tablas."""
    user_creation = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='%(app_label)s_%(class)s_creation',
                                      null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user_updated = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name='%(app_label)s_%(class)s_updated',
                                     null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
```

Todos los modelos de dominio heredan de `BaseModel`. Los campos de auditoría se pueblan con `crum.get_current_user()` en el método `save()` de cada modelo.

---

## 10. `core/utils.py` — format_form_errors()

```python
def format_form_errors(form):
    """Formatea errores del formulario como string legible.
    Retorna: "Campo: error | Otro Campo: error"
    """
    error_list = []
    for field_name, errors in form.errors.items():
        if field_name == '__all__':
            for error in errors:
                error_list.append(str(error))
        else:
            field = form.fields.get(field_name)
            if field and hasattr(field, 'label') and field.label:
                field_label = field.label
            elif hasattr(form.instance._meta.get_field(field_name), 'verbose_name'):
                field_label = form.instance._meta.get_field(field_name).verbose_name
            else:
                field_label = field_name.replace('_', ' ').capitalize()
            for error in errors:
                error_list.append(f"{field_label}: {error}")
    return ' | '.join(error_list)
```

Se usa en todas las vistas para mostrar errores al usuario de forma legible.

---

## 11. `core/validators.py` — Validadores de archivos

```python
import os, re
from django.core.exceptions import ValidationError

def validator_file_image(value):
    """Valida imágenes: max 256KB, .jpg/.png/.svg, nombre alfanumérico."""
    limit = 256 * 1024
    ext = os.path.splitext(value.name)[1]
    namefile = os.path.splitext(os.path.basename(value.name))[0]
    special_character = re.fullmatch('[A-Za-z0-9_!-]+', namefile)
    valid_extensions = ['.jpeg', '.jpg', '.png', '.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Extensión no permitida...')
    if value.size > limit:
        raise ValidationError('Archivo demasiado grande...')
    if not special_character:
        raise ValidationError('Nombre de archivo inválido...')

def validator_file_image_user(value):
    """Igual pero sin validación de nombre de archivo."""
    # similar al anterior, sin regex
```

---

## 12. `core/context_processors.py` — extras_processor

Se registra en settings como `'core.context_processors.extras_processor'`. Inyecta en **todas** las plantillas:

| Variable                  | Descripción                                        |
|---------------------------|----------------------------------------------------|
| `training_expire_count`   | Capacitaciones vencidas del usuario                |
| `count_scheduled_sampling`| Muestreos programados (sitio del lab del usuario)  |
| `count_confirmed_sampling`| Muestreos confirmados                              |
| `count_in_process_sampling`| Muestreos en proceso                              |
| `count_sampling_end`      | Muestreos finalizados (Aprobado/Rechazado)         |
| `count_oos_result`        | Análisis fuera de especificación (No Cumple)       |
| `count_mtto_expire`       | Mantenimientos vencidos                            |
| `count_mtto_expire_responsible` | Mantenimientos vencidos del usuario          |
| `count_calibration_expire`| Calibraciones vencidas                             |
| `count_calibration_expire_responsible` | Calibraciones vencidas del usuario      |
| `count_total_alarm`       | Suma: training + calibraciones + mtto vencidos     |
| `percent_*`               | Porcentajes calculados para cada categoría         |
| `company`                 | Primer registro de Company (para sidebar)          |

**Todas las consultas están acotadas al `site` del laboratorio del usuario.**

---

## 13. Sistema de Signals

### Registro

Los signals se importan en el método `ready()` de `apps.py`:

```python
# core/sampling/apps.py
class SamplingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.sampling'

    def ready(self):
        try:
            import core.sampling.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
```

### Tipos de signals usados

1. **`post_save` en modelos**: para desencadenar acciones cuando cambia el estado de un registro.
   - Ejemplo: al confirmar un `SamplingProcess` (status='Confirmada'), se crean automáticamente los `SamplingAnalysis` para cada método analítico.

2. **Actualización de inventario**: signals que actualizan cantidades en `InventoryReagent` usando `select_for_update()` para evitar race conditions.

3. **Creación de transacciones**: signals que registran entradas en tablas de auditoría o transacciones (ej: `TransactionSolutionStd` al usar solución en un análisis).

### Convención

- Los signals se definen en `signals.py` dentro de cada app
- Se usa el decorador `@receiver(post_save, sender=ModelClass)`
- Lógica de negocio pesada se mantiene en `services.py` y los signals solo orquestan

---

## 14. `services.py` — Capa de lógica de negocio

Separa la lógica compleja de las vistas y signals. Se ubica en `core/<app>/services.py`.

### Ejemplo: `core/sampling/services.py`

Contiene funciones puras (no son clases) para:

- **Generación automática de muestreos** (`generate_samplings_for_group`): crea `SamplingProcess` en lote con `transaction.atomic()`
- **Cálculo de horarios** (`compute_sampling_times`): espacia muestreos según frecuencia configurada
- **Procesamiento de Excel** (`process_massive_analysis_excel`): lee archivos, valida, crea registros en bulk
- **Generación de plantillas Excel** (`build_massive_analysis_template`): crea workbook con openpyxl

### Patrón

```python
# services.py — funciones independientes, sin dependencia de request
from django.db import transaction
from .models import MiModelo

def mi_logica_de_negocio(param1, param2):
    with transaction.atomic():
        # crear, actualizar, validar
        return resultado
```

---

## 15. Custom Template Tags

### `templatetags/path_helpers.py`

Cargado como **built-in** en `TEMPLATES[0]['OPTIONS']['builtins']`. No requiere `{% load %}`.

```python
@register.simple_tag(takes_context=True)
def is_active_section(context, *paths):
    """Retorna 'treeview-item active' si request.path contiene alguno de los paths."""
    request_path = context['request'].path
    return 'treeview-item active' if any(path in request_path for path in paths) else 'treeview-item'

@register.simple_tag(takes_context=True)
def is_expanded(context, *paths):
    """Retorna 'treeview is-expanded' si request.path contiene alguno de los paths."""
    request_path = context['request'].path
    return 'treeview is-expanded' if any(path in request_path for path in paths) else 'treeview'
```

### `templatetags/custom_filters.py`

También cargado como built-in.

```python
@register.filter
def index(sequence, position):
    """Retorna sequence[position] o None si falla."""
    try:
        return sequence[position]
    except (IndexError, TypeError, KeyError):
        return None
```

---

## 16. Configuración de Django (settings.py)

### Aspectos clave

```python
# Apps instaladas: solo apps del core + librerías esenciales
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core.user',       # Custom User model
    'core.start',
    'core.login',
    # ... resto de apps core
    'widget_tweaks',   # Renderizado de formularios
    'django_password_history',  # Historial de contraseñas
]

# Middleware — lo esencial + crum para get_current_user()
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',  # <- Necesario para get_current_user() en modelos
]

# Templates: directorio raíz + subdirectorios de apps
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'core.context_processors.extras_processor',  # Personalizado
        ],
        'builtins': [
            'templatetags.path_helpers',    # is_active_section, is_expanded
            'templatetags.custom_filters',   # index
        ],
    },
}]

# Internacionalización
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_TZ = True
USE_I18N = True

# Auth
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/start/'

# Configuración regional
MESSAGE_TAGS = {
    message_constants.SUCCESS: 'success',
    message_constants.ERROR: 'danger',
    message_constants.WARNING: 'warning',
    message_constants.INFO: 'info',
    message_constants.DEBUG: 'debug',
}
```

### Dependencias pip esenciales

```
Django>=6.0
psycopg2-binary          # PostgreSQL
dj-database-url           # Configuración de BD desde URL
python-decouple           # Variables de entorno (.env)
django-crum               # get_current_user() en cualquier capa
django-widget-tweaks      # Mejoras en renderizado de forms
django-password-history   # Historial de contraseñas
whitenoise                # Archivos estáticos en producción
boto3                     # AWS S3 para media files
xhtml2pdf                 # PDFs desde HTML
reportlab                 # PDFs programáticos
pyHanko                   # Firmas digitales en PDFs
openpyxl                  # Excel (lectura/escritura)
Pillow                    # Imágenes
```

---

## 17. Entorno Virtual y Dependencias

### Creación del entorno

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Archivos de configuración `.env`

Dos archivos (ambos gitignored):

| Archivo       | Leído por          | Propósito                          |
|---------------|--------------------|-------------------------------------|
| `.env` (raíz) | docker compose     | Variables interpoladas en compose   |
| `luka/.env`   | Django (decouple)  | Configuración de desarrollo local   |

Variables típicas en `luka/.env`:

```
SECRET_KEY=xxx
DEBUG=True
DATABASE_URL=postgres://user:pass@host:5432/dbname
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=user@example.com
MAIL_PASSWORD=xxx
DEFAULT_FROM_EMAIL=noreply@example.com
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
BUCKET=my-bucket
REGION_NAME=us-east-1
```

### Comandos principales

```bash
python manage.py runserver              # Desarrollo
python manage.py migrate               # Migraciones
python manage.py createsuperuser       # Admin
python manage.py test                  # Tests
python manage.py test core.sampling    # Tests por app
python manage.py collectstatic         # Estáticos para prod
```

---

## 18. App Pattern: Estructura de cada módulo

```
core/<app_name>/
  __init__.py
  apps.py             # AppConfig con ready() que importa signals
  models.py           # Modelos (heredan BaseModel, PKs UUID)
  forms.py            # Django ModelForms (create + update separados)
  urls.py             # app_name = 'app_name', rutas CRUD con UUID
  views/              # Vistas organizadas por sub-recurso
    __init__.py
    sub_resource/
      __init__.py
      views.py
  admin.py            # Admin registration
  signals.py          # Django signals (post_save, etc.)
  services.py         # Lógica de negocio
  migrations/         # Migraciones
  static/<app_name>/  # JS específicos de la app
  templates/<app_name>/ # Templates específicos
  tests/              # Tests
    __init__.py
    factories.py
    test_models.py
    test_forms.py
    test_services.py
    test_views.py
```

### apps.py mínimo

```python
from django.apps import AppConfig

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.mi_app'

    def ready(self):
        try:
            import core.mi_app.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
```

Si la app no tiene signals, no se define `ready()`.

### urls.py patrón

```python
from django.urls import path
from core.mi_app.views.sub_resource.views import *

app_name = 'mi_app'

urlpatterns = [
    path('add/', MiCreateView.as_view(), name='create_modelo'),
    path('list/', MiListView.as_view(), name='list_modelo'),
    path('update/<uuid:pk>/', MiUpdateView.as_view(), name='update_modelo'),
    path('detail/<uuid:pk>/', MiDetailView.as_view(), name='detail_modelo'),
    path('delete/<uuid:pk>/', MiDeleteView.as_view(), name='delete_modelo'),
]
```

---

## 19. Resumen del Flujo de una Operación CRUD

### Crear (Create)

1. Usuario navega a `/app/list/` → ve DataTable con botón "Nuevo"
2. Botón abre modal (`open_modal('/app/add/')`) o redirige a `/app/add/`
3. Si es modal: se carga `modal_three.html` con el formulario
4. Usuario llena el form y hace submit
5. JavaScript (jQuery AJAX) envía POST con `action='add'` y FormData
6. Vista `CreateView.post()` valida con `form.is_valid()`
7. Si éxito: `JsonResponse({'success': True, 'redirect_url': ...})` → SweetAlert2 → redirección
8. Si error: `JsonResponse({'error': format_form_errors(form)})` → se muestra en SweetAlert2

### Listar (Read con DataTables)

1. Usuario navega a `/app/list/`
2. Vista `ListView` sirve el template que extiende `list_one.html`
3. DataTable se inicializa y hace POST AJAX con `action='searchdata'`
4. Vista responde con `JsonResponse(lista_de_dicts, safe=False)`
5. DataTable renderiza filas usando `columnDefs` con render para acciones (editar, eliminar, detalle)

### Editar (Update)

1. En la DataTable, botón de editar redirige a `/app/update/<uuid>/`
2. Template `create_two.html` se carga con `action='edit'`
3. Submit vía axios POST con `action='edit'`
4. Vista `UpdateView.post()` valida y guarda

### Eliminar (Delete)

1. En la DataTable, botón de eliminar abre modal: `open_modal('/app/delete/<uuid>/')`
2. Se carga `delete_modal.html` con `action='delete'` y `object.id`
3. Usuario confirma → jQuery AJAX POST con `action='delete'` y `id=<uuid>`
4. Vista elimina el objeto y retorna `JsonResponse({})`
5. JS recarga la página: `location.href = window.location.pathname`

---

## 20. Checklist para Replicar en un Proyecto Nuevo

1. **Crear proyecto Django** y configurar `settings.py` con lo de la sección 16
2. **Crear `core/models.py`** con `BaseModel` abstracto
3. **Crear `core/mixins.py`** con `ValidatePermissionRequiredMixin`
4. **Crear `core/utils.py`** con `format_form_errors()`
5. **Crear `core/validators.py`** para validación de archivos
6. **Crear `core/context_processors.py`** y registrarlo en settings
7. **Crear `templatetags/`** con `path_helpers.py` y `custom_filters.py`, registrarlos como builtins
8. **Crear estructura de templates base**:
   - `templates/base.html`
   - `templates/body.html`
   - `templates/header.html`
   - `templates/sidebar.html`
   - `templates/create_one.html`, `create_two.html`, `create_three.html`
   - `templates/list_one.html`
   - `templates/modal_one.html` a `modal_four.html`
   - `templates/delete_modal.html`
9. **Crear primera app `core/user`** con Custom User model (UUID PK)
10. **Instalar dependencias**: `django-crum`, `django-widget-tweaks`, `psycopg2-binary`, `python-decouple`
11. **Para cada nueva app**, crear:
    - `apps.py` (con `ready()` si tiene signals)
    - `models.py` (heredar `BaseModel`)
    - `forms.py` (create + update separados, `col_class`, `get_current_user()`)
    - `views/<sub_resource>/views.py` (CreateView, ListView, UpdateView, DetailView)
    - `urls.py` (app_name, rutas CRUD con UUID)
    - `services.py` (si hay lógica de negocio)
    - `signals.py` (si hay triggers)
    - `admin.py`
    - `templates/<app_name>/` (extienden los layouts base)
    - `static/<app_name>/` (JS de DataTables, validaciones)
12. **Registrar la app** en `INSTALLED_APPS` en settings
13. **Agregar ruta** en `luka/urls.py` con `path('app/', include('core.app.urls'))`
14. **Crear permisos** en migraciones o signals post_migrate (formato: `app_label.action_modelname`)
