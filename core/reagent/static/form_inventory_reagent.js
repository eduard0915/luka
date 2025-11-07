// Script para mostrar/ocultar el campo density y actualizar labels de quantity_stock y purity
// basado en los campos volumetric, umb y purity_unit del Reagent seleccionado

document.addEventListener('DOMContentLoaded', function() {
    const reagentSelect = document.querySelector('select[name="reagent"]');
    const densityInput = document.querySelector('input[name="density"]');
    const quantityStockInput = document.querySelector('input[name="quantity_stock"]');
    const purityInput = document.querySelector('input[name="purity"]');

    if (!reagentSelect || !densityInput || !quantityStockInput || !purityInput) {
        console.error('No se encontraron los campos reagent, density, quantity_stock o purity');
        return;
    }

    // Buscar el contenedor del campo density (div que contiene label + input)
    // Puede ser un div.form-group, div.mb-3, o el padre directo
    const densityContainer = densityInput.closest('.form-group') ||
                            densityInput.closest('.mb-3') ||
                            densityInput.closest('div') ||
                            densityInput.parentElement;

    // Buscar los labels de los campos
    const quantityStockLabel = document.querySelector('label[for="id_quantity_stock"]') ||
                               quantityStockInput.previousElementSibling;

    const purityLabel = document.querySelector('label[for="id_purity"]') ||
                        purityInput.previousElementSibling;

    // Función para verificar si el reactivo es volumétrico y obtener umb y purity_unit
    async function checkReagentInfo(reagentId) {
        if (!reagentId) {
            // Si no hay reactivo seleccionado, ocultar density y resetear labels
            hideDensityField();
            resetQuantityStockLabel();
            resetPurityLabel();
            return;
        }

        try {
            // Realizar petición AJAX para obtener información del reactivo
            const response = await fetch(`/reagent/get-reagent-info/${reagentId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error al obtener información del reactivo');
            }

            const data = await response.json();

            // Si volumetric es True, mostrar el campo density
            if (data.volumetric === true) {
                showDensityField();
            } else {
                hideDensityField();
            }

            // Actualizar el label de quantity_stock con umb
            if (data.umb) {
                updateQuantityStockLabel(data.umb);
            } else {
                resetQuantityStockLabel();
            }

            // Actualizar el label de purity con purity_unit
            if (data.purity_unit) {
                updatePurityLabel(data.purity_unit);
            } else {
                resetPurityLabel();
            }
        } catch (error) {
            console.error('Error:', error);
            // En caso de error, ocultar density y resetear labels
            hideDensityField();
            resetQuantityStockLabel();
            resetPurityLabel();
        }
    }

    // Función para ocultar el campo density
    function hideDensityField() {
        densityContainer.style.display = 'none';
        // Establecer valor por defecto de 1 cuando está oculto
        densityInput.value = '1';
        // Remover el atributo required cuando está oculto
        densityInput.removeAttribute('required');
    }

    // Función para mostrar el campo density
    function showDensityField() {
        densityContainer.style.display = '';
        // Restaurar el atributo required cuando se muestra
        densityInput.setAttribute('required', 'required');
    }

    // Función para actualizar el label de quantity_stock con umb
    function updateQuantityStockLabel(umb) {
        if (quantityStockLabel) {
            // Remover el asterisco rojo si existe
            const requiredSpan = quantityStockLabel.querySelector('.text-danger, .required');
            const asterisk = requiredSpan ? requiredSpan.outerHTML : '';

            quantityStockLabel.innerHTML = `Cantidad (${umb})${asterisk}`;
        }
    }

    // Función para resetear el label de quantity_stock al valor original
    function resetQuantityStockLabel() {
        if (quantityStockLabel) {
            const requiredSpan = quantityStockLabel.querySelector('.text-danger, .required');
            const asterisk = requiredSpan ? requiredSpan.outerHTML : '';

            quantityStockLabel.innerHTML = `Cantidad${asterisk}`;
        }
    }

    // Función para actualizar el label de purity con purity_unit
    function updatePurityLabel(purityUnit) {
        if (purityLabel) {
            // Remover el asterisco rojo si existe
            const requiredSpan = purityLabel.querySelector('.text-danger, .required');
            const asterisk = requiredSpan ? requiredSpan.outerHTML : '';

            purityLabel.innerHTML = `Pureza (${purityUnit})${asterisk}`;
        }
    }

    // Función para resetear el label de purity al valor original
    function resetPurityLabel() {
        if (purityLabel) {
            const requiredSpan = purityLabel.querySelector('.text-danger, .required');
            const asterisk = requiredSpan ? requiredSpan.outerHTML : '';

            purityLabel.innerHTML = `Pureza${asterisk}`;
        }
    }

    // Evento cuando cambia la selección del reactivo
    reagentSelect.addEventListener('change', function() {
        const selectedReagentId = this.value;
        checkReagentInfo(selectedReagentId);
    });

    // Verificar el estado inicial si ya hay un reactivo seleccionado
    if (reagentSelect.value) {
        checkReagentInfo(reagentSelect.value);
    } else {
        // Ocultar el campo y resetear labels por defecto si no hay reactivo seleccionado
        hideDensityField();
        resetQuantityStockLabel();
        resetPurityLabel();
    }
});