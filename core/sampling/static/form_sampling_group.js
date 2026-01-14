document.addEventListener('DOMContentLoaded', function() {
    const samplingPointSelect = document.querySelector('select[name="sampling_point"]');
    const numberSamplingDayInput = document.querySelector('input[name="number_sampling_day"]');

    if (!samplingPointSelect || !numberSamplingDayInput) {
        console.error('No se encontraron los campos necesarios');
        return;
    }

    // Hacer el campo de solo lectura para evitar edición manual
    numberSamplingDayInput.setAttribute('readonly', 'readonly');

    // Función para calcular y actualizar el número de muestras por día
    function calculateSamplingDay() {
        const samplingPointId = samplingPointSelect.value;

        if (!samplingPointId) {
            numberSamplingDayInput.value = '';
            return;
        }

        // Obtener la frecuencia mediante AJAX desde la API
        axios.get(`/sampling/api/sampling-point/${samplingPointId}/`)
            .then(function(response) {
                if (response.data && response.data.sample_frequency) {
                    const sampleFrequency = parseInt(response.data.sample_frequency);

                    if (sampleFrequency > 0) {
                        const samplesPerDay = Math.floor(24 / sampleFrequency);
                        numberSamplingDayInput.value = samplesPerDay;
                    } else {
                        numberSamplingDayInput.value = '';
                    }
                } else {
                    numberSamplingDayInput.value = '';
                }
            })
            .catch(function(error) {
                console.error('Error al obtener la frecuencia:', error);
                numberSamplingDayInput.value = '';
            });
    }

    // Detectar si es Select2 y está inicializado
    if ($(samplingPointSelect).hasClass('select2')) {
        // Esperar a que Select2 se inicialice
        setTimeout(function() {
            if ($(samplingPointSelect).data('select2')) {
                $(samplingPointSelect).on('select2:select', function(e) {
                    calculateSamplingDay();
                });
            } else {
                // Inicializar Select2 si no está inicializado
                $(samplingPointSelect).select2({
                    theme: 'bootstrap-5',
                    width: '100%',
                    placeholder: 'Seleccionar'
                });

                $(samplingPointSelect).on('select2:select', function(e) {
                    calculateSamplingDay();
                });
            }
        }, 100);
    } else {
        // Evento change normal para select sin Select2
        samplingPointSelect.addEventListener('change', function() {
            calculateSamplingDay();
        });
    }

    // Calcular al cargar si ya hay un valor seleccionado (para edición)
    if (samplingPointSelect.value) {
        setTimeout(function() {
            calculateSamplingDay();
        }, 500);
    }
});