// type_test_toggle.js
// Función para controlar la visibilidad de campos según type_test
function toggleFieldsByTypeTest() {
    const typeTestField = $('#id_type_test');
    const typeTestValue = typeTestField.val();

    // Campos de rango
    const lowerLimitField = $('#id_lower_limit_prod').closest('.form-group').parent();
    const upperLimitField = $('#id_upper_limit_prod').closest('.form-group').parent();
    const unitMeasureField = $('#id_unit_measure').closest('.form-group').parent();

    // Campo descriptivo
    const featuresField = $('#id_features_prod').closest('.form-group').parent();

    if (typeTestValue === 'Descriptivo') {
        // Ocultar y deshabilitar campos de rango
        lowerLimitField.hide();
        upperLimitField.hide();
        unitMeasureField.hide();
        $('#id_lower_limit_prod').prop('disabled', true).prop('required', false);
        $('#id_upper_limit_prod').prop('disabled', true).prop('required', false);
        $('#id_unit_measure').prop('disabled', true).prop('required', false);

        // Mostrar y habilitar campo descriptivo
        featuresField.show();
        $('#id_features_prod').prop('disabled', false);

    } else if (typeTestValue === 'Rango') {
        // Mostrar y habilitar campos de rango
        lowerLimitField.show();
        upperLimitField.show();
        unitMeasureField.show();
        $('#id_lower_limit_prod').prop('disabled', false);
        $('#id_upper_limit_prod').prop('disabled', false);
        $('#id_unit_measure').prop('disabled', false);

        // Ocultar y deshabilitar campo descriptivo
        featuresField.hide();
        $('#id_features_prod').prop('disabled', true).prop('required', false);
    }
}

// Ejecutar al cargar la página
$(document).ready(function() {
    toggleFieldsByTypeTest();

    // Ejecutar cuando cambie el valor de type_test
    $('#id_type_test').on('change', function() {
        toggleFieldsByTypeTest();
    });

    // Hook antes de enviar el formulario para habilitar campos
    $('form').on('submit', function() {
        // Habilitar temporalmente todos los campos antes de enviar
        $('#id_lower_limit_prod, #id_upper_limit_prod, #id_unit_measure, #id_features_prod').prop('disabled', false);
    });
});