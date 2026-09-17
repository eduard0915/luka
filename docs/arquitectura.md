# Arquitectura de PadLims (Luka LIMS)

Documento de referencia sobre la arquitectura, organización del código,
estructura de ficheros y patrones de codificación de las vistas CRUD
(`ListView`, `CreateView`, `UpdateView`), formularios, plantillas y
recursos estáticos, tomando como ejemplo la aplicación `core/reagent`.

## 1. Visión general

**PadLims** es un LIMS construido con **Django 6.0** y **PostgreSQL 16**. Sigue un
patrón **MVT (Model-View-Template)** clásico de Django con dos particularidades:

- **Vistas** agrupadas por sub-recurso en un paquete `views/` (no un único `views.py`).
- **Frontend AJAX**: los listados usan **DataTables** con una acción `searchdata`
  (POST → JSON) y los formularios se envían por AJAX (`axios` / `$.ajax`) respondiendo JSON.

El sistema de roles/permisos usa la cadena estándar de Django
`app_label.action_modelname` (p. ej. `reagent.add_reagent`), validada por el mixin
propio `ValidatePermissionRequiredMixin` en `core/mixins.py`.

## 2. Estructura de ficheros (nivel raíz)

```
luka/
├── luka/                    # Proyecto: settings, urls, wsgi/asgi
│   ├── settings.py          # INSTALLED_APPS, TEMPLATES, STATIC*, MEDIA*, AWS S3
│   └── urls.py              # Router principal (incluye cada app bajo /<recurso>/)
├── core/                    # Todas las aplicaciones de dominio
├── templates/               # Plantillas base (layout, CRUD, modales)
├── static/                  # Estáticos globales (lib/vali-admin, lib/fontawesome, css, js)
├── templatetags/            # path_helpers, custom_filters (registrados como builtins)
├── media/                   # Archivos subidos en desarrollo
├── docs/                    # Documentación
└── manage.py
```

### Aplicaciones en `core/`

`core.user`, `core.start`, `core.login`, `core.home`, `core.company`,
`core.reagent`, `core.solution`, `core.laboratory`, `core.equipment`,
`core.product`, `core.analytical_method`, `core.sampling`, `core.condition`,
`core.observation`, `core.report`.

Todas se registran en `luka/settings.py` → `INSTALLED_APPS` y se montan en
`luka/urls.py` con un prefijo propio:

```python
path('reagent/', include('core.reagent.urls')),
```

## 3. Estructura de una aplicación (ejemplo `core/reagent`)

```
core/reagent/
├── __init__.py
├── apps.py                  # AppConfig; ready() importa señales
├── models.py                # Reagent, InventoryReagent, TransactionReagent
├── forms.py                 # ReagentForm, InventoryReagentForm, ...
├── urls.py                  # namespace 'reagent'
├── signals.py               # Señales (si aplica)
├── services.py              # Lógica de negocio (transfers, etc.)
├── views/                   # Paquete de vistas, un subdirectorio por sub-recurso
│   ├── __init__.py
│   ├── reagent/             # CRUD de Reactivo
│   │   └── views.py         # ReagentListView, CreateView, UpdateView, DetailView, DownloadView
│   ├── inventory_reagent/   # CRUD de inventario
│   │   └── views.py
│   └── transaction_reagent/ # Transacciones de reactivo
│       └── views.py
├── static/                  # JS/CSS propios de la app (finders los detectan)
│   ├── list_reagent.js
│   ├── list_inventory_reagent.js
│   └── form_inventory_reagent.js
├── templates/               # Plantillas propias
│   ├── reagent/
│   │   ├── create_reagent.html
│   │   ├── list_reagent.html
│   │   └── detail_reagent.html
│   ├── inventory_reagent/
│   └── transaction_reagent/
├── admin.py
├── migrations/
└── tests/                   # factories.py, test_models.py, test_views.py, ...
```

> **Nota de estáticos**: `core/reagent/static/list_reagent.js` se referencia como
> `{% static 'list_reagent.js' %}`. Django lo resuelve mediante los **staticfiles
> finders** (busca `static/` dentro de cada app), sin necesidad de copiarlo a la
> carpeta global. `STATICFILES_DIRS` solo agrega `static/` del proyecto.

## 4. Modelos: patrón de codificación

Todos los modelos heredan de `core.models.BaseModel`, que provee campos de auditoría:

```python
user_creation, date_creation, user_updated, date_updated
```

Patrón del modelo (ver `core/reagent/models.py`):

```python
class Reagent(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          unique=True, editable=False)
    description_reagent = models.CharField(max_length=200, verbose_name='Descripción')
    code_reagent = models.CharField(max_length=20, verbose_name='Código',
                                    unique=True, blank=True)
    site = models.ForeignKey(Site, verbose_name='Planta', on_delete=models.CASCADE)
    ...

    class Meta:
        verbose_name = 'Reagent'
        verbose_name_plural = 'Reagents'
        db_table = 'Reagent'

    def save(self, *args, **kwargs):
        user = get_current_user()          # django-crum
        if user:
            if not self.user_creation:
                self.user_creation = user  # creación
            else:
                self.user_updated = user   # edición
        if not self.code_reagent:
            with transaction.atomic(using=kwargs.get('using')):
                self.code_reagent = code_reagent_generator()  # secuencia bloqueada
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)
```

Convenciones:
- PK UUID `editable=False`.
- `save()` sobrescrito para poblar `user_creation`/`user_updated` vía `crum.get_current_user()`
  (el middleware `crum.CurrentRequestUserMiddleware` está activo en `settings.py`).
- `verbose_name`/`verbose_name_plural` y `db_table` en español/inglés según se use.
- Generación de códigos secuenciales con `select_for_update()` para evitar carreras.

## 5. Forms: patrón de codificación

Ver `core/reagent/forms.py`. Patrones comunes:

1. **Atributo dinámico `col_class`**: cada campo recibe una clase CSS de columna de
   Bootstrap para el layout de grilla (`col-md-2`, `col-md-5`, …) usada por las
   plantillas `create_two.html` y `modal_three.html`:

```python
col_classes = {'site': 'col-md-2', 'description_reagent': 'col-md-5', ...}
for field_name, field in self.fields.items():
    field.col_class = col_classes.get(field_name, 'col-md-3')
```

2. **Widgets con clases Bootstrap 5** (`form-control`) y `autocomplete='off'` en todos
   los campos visibles.
3. **Listas de selección inline** en módulo (p. ej. `UMB`, `BOOLEAN`, `UNIT_PURITY`,
   `REGISTRY_TYPE`) que se pasan al widget `Select(choices=...)`.
4. **`save(commit=True)` retorna un diccionario** `{ 'error': ... }` o el objeto guardado,
   en lugar de lanzar excepciones; esto se acopla al patrón AJAX de las vistas.
5. **Filtrado por contexto**: `InventoryReagentForm` limita el queryset de `reagent`
   por el sitio del laboratorio del usuario actual (`user.laboratory.site.id`) y
   ajusta etiquetas según el reactivo (`Cantidad (mL)`).

## 6. URLs

Ver `core/reagent/urls.py`. Convenciones:

- `app_name = 'reagent'`.
- Importación `from core.reagent.views.reagent.views import *`.
- Nombres: `create_<model>`, `list_<model>`, `update_<model>`, `detail_<model>`,
  `delete_<model>`.
- Uso de `<uuid:pk>/` para objetos con PK UUID.
- Acciones AJAX/descarga con path propio (`get-reagent-info/<uuid:reagent_id>/`,
  `technical_sheet/`).

```python
urlpatterns = [
    path('add/', ReagentCreateView.as_view(), name='create_reagent'),
    path('list/', ReagentListView.as_view(), name='list_reagent'),
    path('update/<uuid:pk>/', ReagentUpdateView.as_view(), name='update_reagent'),
    path('detail/<uuid:pk>/', ReagentDetailView.as_view(), name='detail_reagent'),
    ...
]
```

## 7. Jerarquía de plantillas

Las plantillas base viven en `templates/` (nivel proyecto) y las específicas en
`<app>/templates/`. Cadena de herencia:

```
base.html
└── body.html                     # header + sidebar + mensajes + modal_template + open_modal()
    ├── create_one.html           # formulario vertical simple (1 campo por fila)
    ├── create_two.html           # formulario en grilla (col_class) + envío axios
    ├── create_three.html
    ├── list_one.html             # tabla #data + DataTables
    ├── detail_one.html
    ├── blank.html / start.html / homepage.html / error_404.html / notperms.html
```

Plantillas de modal (fragmentos que se cargan con `open_modal(url)`):

```
modal_one.html  ...  modal_four.html  (modal_three.html = formulario modal con $.ajax)
delete_modal.html
```

Ejemplo de uso en `core/reagent`:

- `core/reagent/templates/reagent/create_reagent.html`:
  `{% extends 'create_two.html' %}`
- `core/reagent/templates/reagent/list_reagent.html`:
  `{% extends 'list_one.html' %}` + `{% block head_list %}` carga `list_reagent.js` +
  `{% block columns %}` define el `<thead>`.
- `core/reagent/templates/reagent/detail_reagent.html`:
  fragmento modal completo (abre con `open_modal('/reagent/detail/<id>/')`).

### Bloques relevantes de `body.html`

```html
{% block head %}          # CSS + {% block head_list %} (JS/CSS por página)
{% block buttons %}       # botones de acción (ej. "Nuevo")
{% block notifications %} # mensajes Django
{% block content %}       # contenido de la página
{% block scripts_detail %}# JS específico (DataTables, submit AJAX)
```

`body.html` también define la función global `open_modal(url)` que hace `.load(url)`
dentro de `#modal_template` y muestra el modal con Bootstrap.

### Patrón `create_two.html`

- Formulario `id="mainForm"`, `enctype="multipart/form-data"`, `action=""`.
- Cada campo se renderiza en un `<div class="{{ field.field.col_class }}">`.
- Los select `groups`, `is_active`, `site`, `reagent`, `reagent_liquid` se tratan de
  forma especial (solo label + widget) y los campos `file` muestran `help_text`.
- Carga condicional de JS por `entity` (p. ej. `'Registro de Entrada de Reactivos'`
  → `form_inventory_reagent.js`).
- **Envío AJAX con axios**: deshabilita `#btnSubmit` con spinner, POST al path actual
  con `multipart/form-data`, y según `response.data`:
  - `success: true` → SweetAlert y `location.href = data.redirect_url || list_url`.
  - `data.error` → SweetAlert de validación.
  - error de red → SweetAlert de sistema.

### Patrón `list_one.html`

- Contiene la tabla `<table id="data">` con bloques `{% block columns %}` y
  `{% block rows %}`.
- `scripts_detail` carga el plugin de DataTables
  (`lib/vali-admin/js/plugins/jquery.dataTables.min.js`).

### Patrón `modal_three.html`

- Formulario modal `#modal_form`, envío con **`$.ajax`** (jQuery) y `FormData`.
- Helper `format_errors(error)` convierte el dict de errores de Django en HTML para SweetAlert.
- Si la respuesta trae `redirect_url` redirige a ella; si no, recarga la página actual.
- Inicializa **Datepicker** (Bootstrap 5) para inputs con `[data-datepicker="1"]` o
  `.js-datepicker`, envolviéndolos en un `input-group` con botón de calendario.

## 7.1 Cómo estructurar plantillas de tipo formulario (Create/Modal)

Todas las plantillas de formulario del proyecto siguen **una de dos estrategias**:
página completa (heredan de `create_two.html` / `create_one.html`) o **modal**
(herencia de `body.html` y fragmento cargado con `open_modal()`, o directamente un
fragmento como `modal_three.html`). La elección depende de la UX:

| Estrategia      | Plantilla base         | Envío | Uso típico |
|-----------------|------------------------|-------|------------|
| Página completa | `create_two.html`      | axios | CRUD principal (Reactivo, Inventario) |
| Página simple   | `create_one.html`      | axios | Formularios verticales de 1 columna |
| Modal           | `modal_three.html`     | `$.ajax` | Creación/edición desde una lista o detalle |
| Detalle modal   | fragmento (`detail_*.html`) | - | Solo lectura, abierto con `open_modal()` |

### Reglas para crear una plantilla de formulario nueva

1. **Nunca escribir el `<form>` desde cero**: extender `create_two.html` (o el modal
   correspondiente) y solo definir los bloques.
2. **`entity` controla el JS específico**: las plantillas base cargan scripts de forma
   condicional comparando `{{ entity }}` con valores exactos en español
   (p. ej. `'Creación de Reactivo'`). Para no romper esa lógica, el `entity` de la
   vista debe coincidir literalmente con el valor que la plantilla base espera.
3. **Los campos se renderizan automáticamente** iterando `form.visible_fields`; el
   layout de columnas viene de `field.field.col_class` (lo define el form, no la
   plantilla).
4. **Nunca mezclar el JS de submit** en la plantilla de la app: viene ya incluido en
   `create_two.html` / `modal_three.html`. La plantilla de la app solo carga JS de
   lógica de negocio (p. ej. mostrar/ocultar campos, calculadoras) vía `entity`.

### Plantilla mínima de Create/Update (página completa)

`<app>/templates/<recurso>/create_<recurso>.html`:

```django
{% extends 'create_two.html' %}
{% load static %}

{% block head_list %}
    {# CSS/JS de lógica de la página (opcional) #}
{% endblock %}

{% block content %}
    {{ block.super }}   {# solo si se quiere conservar el contenido base #}
{% endblock %}
```

El formulario, el botón Guardar, el `csrf_token`, el `action` oculto y el envío AJAX
con axios ya vienen implementados en `create_two.html`.

### Plantilla mínima de Modal de formulario

`<app>/templates/<recurso>/modal_<recurso>.html` (fragmento; se abre con
`open_modal('/<recurso>/create/')`):

```django
<div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
        <div class="modal-header">
            <h5 class="modal-title">{{ entity }}</h5>
            <p>{{ subtitle }}</p>
            <button class="btn-close" type="button" data-bs-dismiss="modal" aria-label="Close">
                <span aria-hidden="true"></span>
            </button>
        </div>
        <form method="post" action="{{ action_url|default:request.path }}"
              class="form-horizontal" id="modal_form" enctype="multipart/form-data">
            <div class="modal-body">
                {% csrf_token %}
                <input type="hidden" name="action" value="{{ action }}">
                <div class="row">
                    {% for field in form.visible_fields %}
                        <div class="{% if field.field.col_class %}{{ field.field.col_class }}{% else %}col-md-4{% endif %}">
                            <div class="form-group mb-2">
                                <label class="control-label">{{ field.label }}{% if field.field.required %}*{% endif %}</label>
                                {{ field }}
                                {% if field.help_text %}
                                    <small class="form-text text-muted">{{ field.help_text }}</small>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </div>
            <div class="modal-footer">
                <button type="submit" class="btn btn-primary" id="btnSubmit">Guardar</button>
                <button class="btn btn-secondary" type="button" data-bs-dismiss="modal">Cerrar</button>
            </div>
        </form>
    </div>
    {% block scripts_detail %}{% endblock %}
</div>
```

### Cómo decide la plantilla qué JS cargar (`entity`)

En `create_two.html` el bloque `scripts_detail` selecciona el script por `entity`:

```django
{% block scripts_detail %}
    {% if entity == 'Registro de Entrada de Reactivos' %}
        <script src="{% static 'form_inventory_reagent.js' %}"></script>
    {% endif %}
    {% if entity == 'Creación de Grupo de Muestreo' or entity == 'Edición de Grupo de Muestreo' %}
        <script src="{% static 'form_sampling_group.js' %}"></script>
    {% endif %}
    <script src="{% static 'js/datetime.js' %}"></script>
    ... submit AJAX con axios ...
{% endblock %}
```

Convención: **una condición por cada entidad que requiera lógica JS**, comparando el
`entity` exacto que la vista inyecta en el contexto. Para agregar una nueva entidad
basta añadir un `{% if entity == '...' %}`.

### Anatomía del envío AJAX de `create_two.html`

1. `submit` de `#mainForm` → `e.preventDefault()`.
2. Deshabilitar `#btnSubmit` y mostrar spinner (`Guardando...`).
3. `new FormData(this)` → `axios.post(window.location.pathname, parameters, { headers: {'Content-Type': 'multipart/form-data'} })`.
4. Respuesta `response.data`:
   - `success: true` → SweetAlert éxito → `location.href = response.data.redirect_url || '{{ list_url }}'`.
   - `data.error` → SweetAlert "Error de Validación" con HTML de errores.
   - `catch` → SweetAlert "Error del Sistema" y re-habilitar botón.

### Anatomía del envío AJAX de `modal_three.html`

1. `$(document).on('submit', '#modal_form')` (delegación, por si el modal se carga
   después de `DOMContentLoaded`).
2. Mismo patrón de spinner + `$.ajax` con `FormData`, `processData: false`,
   `contentType: false`.
3. `format_errors(data.error)` convierte dict → `<ul>` con cada campo y su error.
4. Éxito → SweetAlert y redirección a `data.redirect_url` o recarga de la página.
5. Al final, inicializa **Datepicker** para `[data-datepicker="1"]` / `.js-datepicker`
   dentro del modal (contenedor = el modal para respetar el z-index).

### Estructura de un modal de Detalle (solo lectura)

`<app>/templates/<recurso>/detail_<recurso>.html` (ver `detail_reagent.html`):

- Mismo envoltorio `modal-dialog` + `modal-header` + `modal-body` + `modal-footer`.
- Sin `<form>`: solo datos de `{{ object }}` agrupados en secciones con
  `<h6 class="section-title">` y pares `<div class="info-label">` / `<p class="info-value">`.
- CSS embebido en `<style>` dentro del `modal-body`.
- Se abre con `open_modal('/<recurso>/detail/<id>/')` (definida en `body.html`).

### Tabla de correspondencia vistas → plantillas

| Vista                    | Plantilla de la app          | Hereda / es   |
|--------------------------|------------------------------|---------------|
| `ReagentCreateView`      | `reagent/create_reagent.html`| `create_two.html` |
| `ReagentUpdateView`      | `reagent/create_reagent.html`| `create_two.html` (misma, `action=edit`) |
| `ReagentListView`        | `reagent/list_reagent.html`  | `list_one.html` |
| `ReagentDetailView`      | `reagent/detail_reagent.html`| fragmento modal |
| `InventoryReagentCreateView` | `inventory_reagent/create_inventory_reagent.html` | `create_two.html` |
| modal de formulario      | `<recurso>/modal_*.html`     | fragmento (patrón `modal_three.html`) |

## 8. JavaScript estático

`core/reagent/static/list_reagent.js` (usado por `list_reagent.html`):

- Se ejecuta en `DOMContentLoaded` (el cuerpo está envuelto por `#data`).
- Inicializa `$('#data').DataTable(...)` con:
  - `responsive: true`, `destroy: true`, `order: [[0, 'desc']]`, `deferRender: true`.
  - Idioma español desde CDN de DataTables.
  - **AJAX**: POST a `window.location.pathname` con `action: 'searchdata'`; el JSON
    de respuesta es directamente el `dataSrc`.
  - `columns` mapeadas 1:1 con los campos devueltos por la vista.
  - `columnDefs`:
    - `targets [5]` (estado) → badge `Activo/Inactivo`.
    - `targets [6]` (ficha) → enlace de descarga a
      `/reagent/technical_sheet/?id=...&type=technical_sheet`.
    - `targets [7,8,9,10]` → render `Si/No` para booleanos.
    - `targets [11]` (acciones) → botón editar (`/reagent/update/<id>/`) y detalle
      (`open_modal('/reagent/detail/<id>/')`).
- Guarda `if (typeof $ !== 'undefined')` para evitar errores si jQuery no cargó.

## 9. CSS

- Proyecto: `static/css/` (`style-card-start.css`, `my_styles.css`, `timepicker.css`).
- Tema base: `static/lib/vali-admin/css/main.css` (tema Vali Admin).
- Iconos: Font Awesome (`static/lib/fontawesome-free-7.1.0/`) y Bootstrap Icons (CDN).
- DataTables: `static/lib/datatables/`.
- CSS embebido para modales de detalle (p. ej. clases `.info-label`, `.info-value`,
  `.section-title` dentro de `detail_reagent.html`).
- `body.html` carga `css/style-card-start.css` en `{% block head %}`.

## 10. Patrón de vista ListView (ReagentListView)

```python
class ReagentListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Reagent
    template_name = 'reagent/list_reagent.html'
    permission_required = 'reagent.view_reagent'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                if request.user.laboratory:
                    data = list(Reagent.objects.values(
                        'id', 'code_reagent', 'description_reagent', 'umb', ...)
                        .filter(site=request.user.laboratory.site).order_by('code_reagent'))
                else:
                    data = []
                return JsonResponse(data, safe=False)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reactivos'
        context['create_url'] = reverse_lazy('reagent:create_reagent')
        context['entity'] = 'Reactivos'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context
```

Características del patrón:

- **GET** no se sobrescribe: `get_context_data` inyecta el contexto de la plantilla
  (`title`, `entity`, `create_url`, `div`, `icon`).
- **POST** responde a `action='searchdata'` devolviendo un **array JSON de dicts**
  (de ahí `safe=False`), filtrado por el sitio del laboratorio del usuario actual.
- **El renderizado de filas lo hace DataTables en cliente** desde ese JSON; por eso el
  bloque `{% block rows %}` de `list_reagent.html` está vacío.
- `csrf_exempt` en `dispatch` (vía `@method_decorator`) para simplificar el POST AJAX
  (el proyecto ya depende de CSRF a nivel de sesión/header).
- Usa `values(...)` en lugar de objetos ORM para serializar directo a JSON.

## 11. Patrón de vista CreateView (ReagentCreateView)

```python
class ReagentCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'
    success_url = reverse_lazy('reagent:list_reagent')
    permission_required = 'reagent.add_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = None          # imprescindible en CreateView
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
                    messages.success(request, f'Reactivo "{...}" creado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de Reactivos'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['entity'] = 'Creación de Reactivo'
        context['div'] = '12'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context
```

Puntos clave:

- `dispatch` fija `self.object = None` (requisito de Django para `CreateView`).
- El `post` procesa la acción `add` y **siempre retorna `JsonResponse`**, nunca un
  `HttpResponseRedirect`; la redirección la hace el JS (`data.redirect_url`).
- Usa `format_form_errors(form)` (`core/utils.py`) para serializar errores a HTML.
- `entity` se usa como disparador para cargar JS condicional en las plantillas base.

## 12. Patrón de vista UpdateView (ReagentUpdateView)

```python
class ReagentUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Reagent
    form_class = ReagentForm
    template_name = 'reagent/create_reagent.html'   # reutiliza la plantilla de creación
    success_url = reverse_lazy('reagent:list_reagent')
    permission_required = 'reagent.change_reagent'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()   # carga el objeto a editar
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
                    messages.success(request, f'Reactivo "{...}" actualizado satisfactoriamente!')
                else:
                    data['error'] = format_form_errors(form)
            else:
                data['error'] = 'No ha ingresado datos en los campos'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar de Reactivos'
        context['list_url'] = self.success_url
        context['entity'] = 'Editar Reactivo'
        context['action'] = 'edit'          # distinto de 'add'
        context['div'] = '10'
        context['icon'] = 'fa-solid fa-flask-vial'
        return context
```

Diferencias con el CreateView:

- `self.object = self.get_object()` en `dispatch`.
- Acción `edit` en lugar de `add` (ambas reutilizan el mismo `ReagentForm`).
- Reutiliza `template_name = 'reagent/create_reagent.html'`; la plantilla es idéntica
  y el cambio de comportamiento viene del contexto (`action='edit'`).
- Permiso `change_reagent`.

## 13. Permisos y mixin

`core/mixins.py` → `ValidatePermissionRequiredMixin`:

- Atributos `permission_required` y `url_redirect`.
- `dispatch()` verifica `request.user.has_perms(...)`; si falla, redirige a
  `url_redirect` (por defecto `start:notperms`).
- Se combina con `LoginRequiredMixin` en el orden
  `class V(LoginRequiredMixin, ValidatePermissionRequiredMixin, View)`.

Cadena de permisos por acción (estándar Django, vía `Group`/`Permission`):
`add_<modelo>`, `view_<modelo>`, `change_<modelo>`, `delete_<modelo>`.

## 14. Flujo completo de un CRUD (Reactivo)

1. **Listar** (`GET /reagent/list/`): `ReagentListView` → `list_reagent.html`
   (extiende `list_one.html`) → carga `list_reagent.js` → DataTables.
2. **Consultar datos** (`POST /reagent/list/`, `action=searchdata`): la vista devuelve
   el JSON con los reactivos del sitio; DataTables lo renderiza; acciones de fila:
   editar (`/reagent/update/<id>/`) y detalle (`open_modal('/reagent/detail/<id>/')`).
3. **Crear** (`GET /reagent/add/`): `ReagentCreateView` → `create_reagent.html`
   (extiende `create_two.html`) → `ReagentForm`.
   Al enviar (`POST /reagent/add/`, `action=add`) axios envía el form; la vista guarda
   y responde `{success, redirect_url}`; el JS muestra SweetAlert y redirige.
4. **Editar** (`GET /reagent/update/<pk>/`): `ReagentUpdateView` → misma plantilla de
   creación, `action=edit`; el `dispatch` carga el objeto y el form llega pre-poblado.
5. **Detalle** (`GET /reagent/detail/<pk>/`): fragmento modal con el objeto; se muestra
   vía `open_modal()` en `body.html`.
6. **Descarga de ficha** (`GET /reagent/technical_sheet/?id=&type=`): `ReagentDownloadView`
   genera una URL prefirmada de S3 y devuelve el archivo con `Content-Disposition`.

## 15. Buenas prácticas / convenciones para nuevas vistas

- Heredar siempre de `LoginRequiredMixin, ValidatePermissionRequiredMixin, <Vista>`.
- `permission_required` con la sintaxis `'app_label.action_modelname'`.
- Sobrescribir `dispatch` con `@method_decorator(csrf_exempt)` y setear `self.object`.
- `post` siempre devuelve `JsonResponse`; usar `data['error']` para errores y
  `data['success']`/`data['redirect_url']` para éxito.
- `get_context_data` inyecta siempre `title`, `entity`, `icon`, `div` y los urls
  (`list_url`/`create_url`).
- Los formularios exponen `field.col_class` para el layout de grilla.
- Los listados devuelven `values(...)` filtrados por el sitio del laboratorio del
  usuario (`request.user.laboratory.site`).
- Mensajes al usuario con el framework `messages` + SweetAlert en el cliente.
- No duplicar `views.py` plano: agrupar por sub-recurso bajo `views/`.