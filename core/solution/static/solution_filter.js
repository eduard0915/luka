// solution_filter.js
(function() {
    'use strict';

    function initSolutionFilters(entity) {
        const select_base = entity === 'Preparar Solución'
            ? $('select[name="solution_base"]')
            : $('select[name="solution_std_base"]');

        const select_solute = entity === 'Preparar Solución'
            ? $('select[name="solute_reagent"]')
            : $('select[name="solute_std"]');

        const select_solvent = $('select[name="solvent_reagent"]');

        function filterOptions(select, reagentId) {
            if (!select.length) return;

            let dataReagents = select.attr('data-reagents');
            if (dataReagents) {
                try {
                    dataReagents = JSON.parse(dataReagents.replace(/'/g, '"'));
                } catch (e) {
                    console.error("Error parsing data-reagents", e);
                    return;
                }
            } else {
                return;
            }

            let firstValid = null;
            select.find('option').each(function () {
                const option = $(this);
                const val = option.val();
                if (!val) return; // Skip placeholder

                const associatedReagentId = dataReagents[val];
                if (associatedReagentId === reagentId) {
                    option.show().prop('disabled', false);
                    if (!firstValid) firstValid = val;
                } else {
                    option.hide().prop('disabled', true);
                }
            });

            // Si el valor actual no es válido, cambiar al primero válido o vacío
            const currentVal = select.val();
            if (currentVal && dataReagents[currentVal] !== reagentId) {
                select.val(firstValid || "").trigger('change');
            } else if (!currentVal && firstValid) {
                // Opcional: auto-seleccionar si solo hay uno?
                // select.val(firstValid).trigger('change');
            }

            // Si usa select2, hay que destruir y recrear o simplemente disparar change
            if (select.hasClass('select2-hidden-accessible')) {
                // select.select2('destroy').select2({theme: 'bootstrap-5'});
            }
        }

        select_base.on('change', function () {
            const id = $(this).val();
            if (!id) return false;

            $.ajax({
                url: '/solution/api/solution-base/' + id + '/',
                type: 'GET',
                dataType: 'json'
            }).done(function (data) {
                if (!data.error) {
                    // Filtrar opciones
                    filterOptions(select_solute, data.solute_reagent_id);
                    if (data.solvent_reagent_id) {
                        filterOptions(select_solvent, data.solvent_reagent_id);
                    }

                    // Opcionalmente llenar concentración si existen los campos
                    const input_conc = entity === 'Preparar Solución'
                        ? $('input[name="concentration"]')
                        : $('input[name="concentration_std"]');
                    const select_unit = $('select[name="concentration_unit"]');

                    if (input_conc.length && data.concentration) {
                        input_conc.val(data.concentration);
                    }
                    if (select_unit.length && data.concentration_unit) {
                        select_unit.val(data.concentration_unit).trigger('change');
                    }

                } else {
                    console.error(data.error);
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.error(textStatus + ': ' + errorThrown);
            });
        });
    }

    // Exponer la función globalmente
    window.initSolutionFilters = initSolutionFilters;

})();