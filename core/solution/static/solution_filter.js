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

        function setSoluteDisabled(disabled) {
            select_solute.prop('disabled', disabled);
            if (disabled) {
                select_solute.val('');
            }
        }

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
                if (!val) return;

                const associatedReagentId = dataReagents[val];
                if (associatedReagentId === reagentId) {
                    option.show().prop('disabled', false);
                    if (!firstValid) firstValid = val;
                } else {
                    option.hide().prop('disabled', true);
                }
            });

            const currentVal = select.val();
            if (currentVal && dataReagents[currentVal] !== reagentId) {
                select.val(firstValid || "").trigger('change');
            }
        }

        // Initial state: disable solute until a base is selected
        setSoluteDisabled(true);
        if (select_solvent.length) {
            select_solvent.prop('disabled', true);
        }

        select_base.on('change', function () {
            const id = $(this).val();
            if (!id) {
                setSoluteDisabled(true);
                if (select_solvent.length) {
                    select_solvent.prop('disabled', true).val('');
                }
                return false;
            }

            $.ajax({
                url: '/solution/api/solution-base/' + id + '/',
                type: 'GET',
                dataType: 'json'
            }).done(function (data) {
                if (!data.error) {
                    filterOptions(select_solute, data.solute_reagent_id);
                    setSoluteDisabled(false);

                    if (data.solvent_reagent_id) {
                        filterOptions(select_solvent, data.solvent_reagent_id);
                        select_solvent.prop('disabled', false);
                    }

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

        // If a base is already selected (update form), trigger the filter on load
        if (select_base.val()) {
            select_base.trigger('change');
        }
    }

    window.initSolutionFilters = initSolutionFilters;

})();