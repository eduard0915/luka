/**
 * form_sampling_process.js
 * Maneja la lógica de mostrar/ocultar campos según el tipo de muestreo
 */

(function() {
    'use strict';

    // Función para obtener el contenedor del campo
    function getFieldContainer(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        return field ? field.closest('.col-md-3, .col-md-2, .col-md-4, [class*="col-md-"]') : null;
    }

    // Función para mostrar/ocultar campos según el tipo de muestreo
    function toggleFieldsByType(typeValue) {
        const groupContainer = getFieldContainer('group_sampling');
        const pointContainer = getFieldContainer('point_sampling');
        const batchContainer = getFieldContainer('batch_number');

        if (!groupContainer || !pointContainer || !batchContainer) {
            console.warn('No se encontraron todos los contenedores de campos');
            return;
        }

        if (typeValue === 'En Proceso') {
            // En Proceso: mostrar group_sampling, ocultar point_sampling y batch_number
            groupContainer.style.display = '';
            pointContainer.style.display = 'none';
            batchContainer.style.display = 'none';

            // Limpiar valores de campos ocultos y disparar evento change para Select2
            const pointField = $('[name="point_sampling"]');
            const batchField = document.querySelector('[name="batch_number"]');
            if (pointField.length) {
                pointField.val('').trigger('change');
            }
            if (batchField) batchField.value = '';

        } else if (typeValue === 'Producto Terminado') {
            // Producto Terminado: mostrar point_sampling y batch_number, ocultar group_sampling
            groupContainer.style.display = 'none';
            pointContainer.style.display = '';
            batchContainer.style.display = '';

            // Limpiar valor de campo oculto y disparar evento change para Select2
            const groupField = $('[name="group_sampling"]');
            if (groupField.length) {
                groupField.val('').trigger('change');
            }

        } else {
            // Si no hay selección o valor desconocido, mostrar todos
            groupContainer.style.display = '';
            pointContainer.style.display = '';
            batchContainer.style.display = '';
        }
    }

    // Inicializar cuando el DOM esté listo
    function init() {
        const typeField = document.querySelector('[name="type_sampling"]');

        if (!typeField) {
            console.warn('Campo type_sampling no encontrado');
            return;
        }

        // Aplicar lógica al cargar la página (por si hay un valor preseleccionado)
        toggleFieldsByType(typeField.value);

        // Escuchar cambios en el campo type_sampling
        typeField.addEventListener('change', function() {
            toggleFieldsByType(this.value);
        });

        console.log('form_sampling_process.js inicializado correctamente');
    }

    // Ejecutar cuando el DOM esté completamente cargado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();