// Manejo del campo sample_frequency basado en la periodicidad seleccionada
$(document).ready(function() {
    const $periodicity = $('select[name="periodicity"]');
    const $sampleFrequency = $('select[name="sample_frequency"]');

    // Periodicidades que requieren readonly
    const readonlyPeriodicities = ['Semanal', 'Quincenal', 'Mensual'];

    function toggleSampleFrequency() {
        const selectedPeriodicity = $periodicity.val();

        if (readonlyPeriodicities.includes(selectedPeriodicity)) {
            // Cambiar el valor a 'No Aplica' (valor vacío)
            $sampleFrequency.val('');

            // Hacer el campo readonly
            $sampleFrequency.prop('readonly', true);
            $sampleFrequency.prop('disabled', true);
            $sampleFrequency.css({
                'background-color': '#e9ecef',
                'cursor': 'not-allowed'
            });
        } else {
            // Habilitar el campo
            $sampleFrequency.prop('readonly', false);
            $sampleFrequency.prop('disabled', false);
            $sampleFrequency.css({
                'background-color': '',
                'cursor': ''
            });
        }
    }

    // Ejecutar al cargar la página
    toggleSampleFrequency();

    // Ejecutar cuando cambie la periodicidad
    $periodicity.on('change', function() {
        toggleSampleFrequency();
    });

    // Asegurar que el campo deshabilitado no se envíe como disabled
    // para que su valor sea incluido en el formulario
    $('form').on('submit', function() {
        $sampleFrequency.prop('disabled', false);
    });
});