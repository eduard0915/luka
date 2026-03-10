$(function () {
    const select_condition = $('select[name="condition"]');
    const registered_data_label = $('label[for="id_registered_data"]');
    const is_required = registered_data_label.text().includes('*');

    if (select_condition.hasClass('select2')) {
        select_condition.select2({
            theme: 'bootstrap-5',
            language: 'es',
            placeholder: 'Seleccione una condición'
        });
    }

    let current_limits = {upper: null, lower: null};
    const input_registered_data = $('input[name="registered_data"]');

    function updateLabel(condition_id) {
        if (condition_id) {
            $.ajax({
                url: '/condition/variable/api/',
                type: 'POST',
                data: {
                    'action': 'get_variable',
                    'id': condition_id
                },
                dataType: 'json',
            }).done(function (data) {
                let labelText = 'Dato Registrado';
                if (!data.hasOwnProperty('error')) {
                    const variable = data.variable.toString().toLowerCase().trim();
                    if (variable.includes('temperatura')) {
                        labelText = 'Registrar Lectura °C';
                    } else if (variable.includes('humedad relativa')) {
                        labelText = 'Registrar Lectura %HR';
                    }
                    current_limits.upper = parseFloat(data.upper_limit);
                    current_limits.lower = parseFloat(data.lower_limit);
                    checkRange();
                }
                registered_data_label.text(labelText + (is_required ? '*' : ''));
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.error(textStatus + ': ' + errorThrown);
            });
        } else {
            registered_data_label.text('Dato Registrado' + (is_required ? '*' : ''));
            current_limits = {upper: null, lower: null};
            checkRange();
        }
    }

    function checkRange() {
        const value = parseFloat(input_registered_data.val());
        if (!isNaN(value) && current_limits.upper !== null && current_limits.lower !== null) {
            if (value > current_limits.upper || value < current_limits.lower) {
                input_registered_data.addClass('is-invalid');
                if (!$('#range-warning').length) {
                    input_registered_data.after('<div id="range-warning" class="invalid-feedback">El dato está fuera de rango (' + current_limits.lower + ' - ' + current_limits.upper + ')</div>');
                }
            } else {
                input_registered_data.removeClass('is-invalid');
                $('#range-warning').remove();
            }
        } else {
            input_registered_data.removeClass('is-invalid');
            $('#range-warning').remove();
        }
    }

    input_registered_data.on('input', function () {
        checkRange();
    });

    select_condition.on('change', function () {
        const id = $(this).val();
        updateLabel(id);
    });

    // Ejecutar al cargar si ya tiene un valor (para el UpdateView)
    if (select_condition.val()) {
        updateLabel(select_condition.val());
    }
});
