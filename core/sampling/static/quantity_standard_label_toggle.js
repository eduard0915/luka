$(document).ready(function() {
    const standardSolutionSelect = $('select[name="standard_solution"]');
    const quantityStandardField = $('input[name="quantity_standard"]');
    const quantityStandardLabel = quantityStandardField.closest('.form-group').find('label.control-label');

    // Función para actualizar el label
    function updateQuantityStandardLabel() {
        const selectedSolutionId = standardSolutionSelect.val();

        if (!selectedSolutionId) {
            // Label por defecto si no hay selección
            quantityStandardLabel.html('Cantidad de Estándar<span style="color: red;">*</span>');
            return;
        }

        // Hacer petición AJAX para obtener la unidad de medida
        $.ajax({
            url: '/sampling/get-solution-std-unit/', // Debes crear esta URL en tu urls.py
            type: 'GET',
            data: {
                'solution_id': selectedSolutionId
            },
            dataType: 'json',
            success: function(data) {
                if (data.unit) {
                    // Actualizar el label con la unidad obtenida
                    quantityStandardLabel.html(`${data.unit} de Estándar<span style="color: red;">*</span>`);
                } else {
                    quantityStandardLabel.html('Cantidad de Estándar<span style="color: red;">*</span>');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error al obtener la unidad:', error);
                quantityStandardLabel.html('Cantidad de Estándar<span style="color: red;">*</span>');
            }
        });
    }

    // Ejecutar al cambiar la solución estándar
    standardSolutionSelect.on('change', updateQuantityStandardLabel);

    // Ejecutar al cargar si ya hay una solución seleccionada
    if (standardSolutionSelect.val()) {
        updateQuantityStandardLabel();
    }
});