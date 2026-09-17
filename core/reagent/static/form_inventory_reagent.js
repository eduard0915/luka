// Script para mostrar/ocultar el campo density y actualizar labels de quantity_stock y purity
// basado en los campos volumetric, umb y purity_unit del Reagent seleccionado

$(document).ready(function() {
    const $reagentSelect = $('select[name="reagent"]');
    const $densityInput = $('input[name="density"]');
    const $quantityStockInput = $('input[name="quantity_stock"]');
    const $purityInput = $('input[name="purity"]');

    if (!$reagentSelect.length || !$densityInput.length || !$quantityStockInput.length || !$purityInput.length) {
        console.error('No se encontraron los campos reagent, density, quantity_stock o purity');
        return;
    }

    const densityContainer = $densityInput.closest('.form-group').length
        ? $densityInput.closest('.form-group')
        : $densityInput.closest('.mb-3').length
            ? $densityInput.closest('.mb-3')
            : $densityInput.parent();

    const $quantityStockLabel = $('label[for="id_quantity_stock"]').length
        ? $('label[for="id_quantity_stock"]')
        : $quantityStockInput.prev();

    const $purityLabel = $('label[for="id_purity"]').length
        ? $('label[for="id_purity"]')
        : $purityInput.prev();

    async function checkReagentInfo(reagentId) {
        if (!reagentId) {
            hideDensityField();
            resetQuantityStockLabel();
            resetPurityLabel();
            return;
        }

        try {
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

            if (data.volumetric === true) {
                showDensityField();
            } else {
                hideDensityField();
            }

            if (data.umb) {
                updateQuantityStockLabel(data.umb);
            } else {
                resetQuantityStockLabel();
            }

            if (data.purity_unit) {
                updatePurityLabel(data.purity_unit);
            } else {
                resetPurityLabel();
            }
        } catch (error) {
            console.error('Error:', error);
            hideDensityField();
            resetQuantityStockLabel();
            resetPurityLabel();
        }
    }

    function hideDensityField() {
        densityContainer.hide();
        $densityInput.val('1');
        $densityInput.removeAttr('required');
    }

    function showDensityField() {
        densityContainer.show();
        $densityInput.attr('required', 'required');
    }

    function updateQuantityStockLabel(umb) {
        if ($quantityStockLabel.length) {
            const $asterisk = $quantityStockLabel.find('.text-danger, .required');
            const asteriskHtml = $asterisk.length ? $asterisk[0].outerHTML : '';
            $quantityStockLabel.html(`Cantidad (${umb})${asteriskHtml}`);
        }
    }

    function resetQuantityStockLabel() {
        if ($quantityStockLabel.length) {
            const $asterisk = $quantityStockLabel.find('.text-danger, .required');
            const asteriskHtml = $asterisk.length ? $asterisk[0].outerHTML : '';
            $quantityStockLabel.html(`Cantidad${asteriskHtml}`);
        }
    }

    function updatePurityLabel(purityUnit) {
        if ($purityLabel.length) {
            const $asterisk = $purityLabel.find('.text-danger, .required');
            const asteriskHtml = $asterisk.length ? $asterisk[0].outerHTML : '';
            $purityLabel.html(`Pureza (${purityUnit})${asteriskHtml}`);
        }
    }

    function resetPurityLabel() {
        if ($purityLabel.length) {
            const $asterisk = $purityLabel.find('.text-danger, .required');
            const asteriskHtml = $asterisk.length ? $asterisk[0].outerHTML : '';
            $purityLabel.html(`Pureza${asteriskHtml}`);
        }
    }

    $reagentSelect.on('change', function() {
        checkReagentInfo(this.value);
    });

    if ($reagentSelect.val()) {
        checkReagentInfo($reagentSelect.val());
    } else {
        hideDensityField();
        resetQuantityStockLabel();
        resetPurityLabel();
    }
});