(function () {
    // Campos numéricos: deben existir y ser > 0
    const NUMERIC_FIELDS = ['milliliter_std_add', 'milliliter_std_spend', 'quantity_sample'];
    // Campos select2: deben tener un valor seleccionado
    const SELECT_FIELDS = ['standard_solution_add', 'standard_solution_spend'];

    function clearFieldError(fieldName) {
        const $input = $('#id_' + fieldName);
        $input.removeClass('is-invalid');
        $('#error-' + fieldName).text('');
    }

    function setFieldError(fieldName, message) {
        const $input = $('#id_' + fieldName);
        $input.addClass('is-invalid');
        $('#error-' + fieldName).text(message);
    }

    function validateMillimoleForm() {
        let isValid = true;

        NUMERIC_FIELDS.forEach(function (fieldName) {
            clearFieldError(fieldName);
            const $input = $('#id_' + fieldName);
            if (!$input.length) return;

            const rawValue = $input.val();
            const value = parseFloat(rawValue);

            if (rawValue === '' || rawValue === null || isNaN(value) || value <= 0) {
                setFieldError(fieldName, 'Este campo es obligatorio y debe ser mayor a cero.');
                isValid = false;
            }
        });

        SELECT_FIELDS.forEach(function (fieldName) {
            clearFieldError(fieldName);
            const $input = $('#id_' + fieldName);
            if (!$input.length) return;

            const value = $input.val();
            if (!value) {
                setFieldError(fieldName, 'Debe seleccionar una opción.');
                isValid = false;
            }
        });

        return isValid;
    }

    // Captura ANTES de que el handler de submit de jQuery (bubbling) dispare el AJAX
    document.addEventListener('submit', function (e) {
        if (e.target && e.target.id === 'modal_form') {
            if (!validateMillimoleForm()) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        }
    }, true);

    // También intercepta el click del botón (que dispara $(this).submit() manualmente)
    document.addEventListener('click', function (e) {
        if (e.target && e.target.id === 'btnSubmit') {
            if (!validateMillimoleForm()) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        }
    }, true);

    // Limpia el error de un campo apenas el usuario empieza a corregirlo
    $(document).on('input change', '#id_milliliter_std_add, #id_milliliter_std_spend, #id_quantity_sample, #id_standard_solution_add, #id_standard_solution_spend', function () {
        clearFieldError($(this).attr('name'));
    });
})();