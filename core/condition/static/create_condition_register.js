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
                }
                registered_data_label.text(labelText + (is_required ? '*' : ''));
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.error(textStatus + ': ' + errorThrown);
            });
        } else {
            registered_data_label.text('Dato Registrado' + (is_required ? '*' : ''));
        }
    }

    select_condition.on('change', function () {
        const id = $(this).val();
        updateLabel(id);
    });

    // Ejecutar al cargar si ya tiene un valor (para el UpdateView)
    if (select_condition.val()) {
        updateLabel(select_condition.val());
    }
});
