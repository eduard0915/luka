$(function () {
    const select_condition = $('select[name="condition"]');
    const select_condition2 = $('select[name="condition2"]');
    const input_registered_data = $('input[name="registered_data"]');
    const input_registered_data2 = $('input[name="registered_data2"]');

    const registered_data_label = $('label[for="id_registered_data"]');
    const registered_data2_label = $('label[for="id_registered_data2"]');

    const is_required1 = registered_data_label.text().includes('*');
    const is_required2 = registered_data2_label.text().includes('*');

    if (registered_data_label.length) {
        registered_data_label.data('original', registered_data_label.text().replace('*', '').trim());
    }
    if (registered_data2_label.length) {
        registered_data2_label.data('original', registered_data2_label.text().replace('*', '').trim());
    }

    function initSelect2(element) {
        if (element.hasClass('select2')) {
            element.select2({
                theme: 'bootstrap-5',
                language: 'es',
                placeholder: 'Seleccione una condición'
            });
        }
    }

    initSelect2(select_condition);
    initSelect2(select_condition2);

    let limits1 = {upper: null, lower: null};
    let limits2 = {upper: null, lower: null};

    function updateLabel(condition_id, label_element, limits_obj, input_element, isSecond) {
        const isRequired = isSecond ? is_required2 : is_required1;
        const originalText = label_element.data('original') || (isSecond ? 'Dato Registrado 2' : 'Dato Registrado');

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
                let labelText = isSecond ? 'Dato Registrado 2' : 'Dato Registrado';
                if (!data.hasOwnProperty('error')) {
                    const variable = data.variable.toString().toLowerCase().trim();
                    if (variable.includes('temperatura')) {
                        labelText = isSecond ? 'Registrar Lectura °C 2' : 'Registrar Lectura °C';
                    } else if (variable.includes('humedad relativa')) {
                        labelText = isSecond ? 'Registrar Lectura %HR 2' : 'Registrar Lectura %HR';
                    }
                    limits_obj.upper = parseFloat(data.upper_limit);
                    limits_obj.lower = parseFloat(data.lower_limit);
                } else {
                    limits_obj.upper = null;
                    limits_obj.lower = null;
                }

                label_element.text(labelText + (isRequired ? ' *' : ''));
                checkRange(input_element, limits_obj);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.error(textStatus + ': ' + errorThrown);
            });
        } else {
            label_element.text(originalText + (isRequired ? ' *' : ''));
            limits_obj.upper = null;
            limits_obj.lower = null;
            checkRange(input_element, limits_obj);
        }
    }

    function checkRange(input_element, limits_obj) {
        const value = parseFloat(input_element.val());
        const warning_id = 'range-warning-' + input_element.attr('name');
        if (!isNaN(value) && limits_obj.upper !== null && limits_obj.lower !== null) {
            if (value > limits_obj.upper || value < limits_obj.lower) {
                input_element.addClass('is-invalid');
                if (!$('#' + warning_id).length) {
                    input_element.parent().append('<div id="' + warning_id + '" class="invalid-feedback">El dato está fuera de rango (' + limits_obj.lower + ' - ' + limits_obj.upper + ')</div>');
                }
            } else {
                input_element.removeClass('is-invalid');
                $('#' + warning_id).remove();
            }
        } else {
            input_element.removeClass('is-invalid');
            $('#' + warning_id).remove();
        }
    }

    input_registered_data.on('input', function () {
        checkRange(input_registered_data, limits1);
    });

    input_registered_data2.on('input', function () {
        checkRange(input_registered_data2, limits2);
    });

    select_condition.on('change', function () {
        updateLabel($(this).val(), registered_data_label, limits1, input_registered_data, false);
    });

    select_condition2.on('change', function () {
        updateLabel($(this).val(), registered_data2_label, limits2, input_registered_data2, true);
    });

    if (select_condition.val()) {
        updateLabel(select_condition.val(), registered_data_label, limits1, input_registered_data, false);
    }
    if (select_condition2.val()) {
        updateLabel(select_condition2.val(), registered_data2_label, limits2, input_registered_data2, true);
    }

});
