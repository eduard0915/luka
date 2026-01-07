// Asegurarse de que jQuery esté definido antes de usar $
document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 0, "desc" ]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
            },
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'searchdata'
                },
                dataSrc: ""
            },
            columns: [
                {'data': 'solute_reagent_base__description_reagent'},
                {'data': 'concentration_base'},
                {'data': 'enable_solution'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'td-actions text-left'
                },
                {
                    targets: [1],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['concentration_base'] + ' ' + row['concentration_unit_base'];
                    }
                },
                {
                    targets: [2],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        switch (row['enable_solution']) {
                            case true:
                                return '<span class="badge bg-primary rounded-pill">Activo</span>';
                            case false:
                                return '<span class="badge bg-danger rounded-pill">Inactivo</span>';
                        }
                    }
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/solution/update_base/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a> &nbsp;';
                        
                        if (row['enable_solution']) {
                            actions += '<a onclick="change_status(\'/solution/disable_base/' + row['id'] + '/\')" type="button" title="Deshabilitar"><i class="bi bi-toggle-on text-primary"></i></a>';
                        } else {
                            actions += '<a onclick="change_status(\'/solution/enable_base/' + row['id'] + '/\')" type="button" title="Habilitar"><i class="bi bi-toggle-off text-danger"></i></a>';
                        }
                        
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});

function change_status(url) {
    $.ajax({
        url: url,
        type: 'POST',
        data: {
            'action': 'change_status'
        },
        dataType: 'json',
    }).done(function (data) {
        if (!data.hasOwnProperty('error')) {
            location.reload();
            return false;
        }
        alert(data.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {

    });
}