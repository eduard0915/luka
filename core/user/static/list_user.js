$(document).ready(function($) {
    $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
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
            {'data': 'first_name'},
            {'data': 'username'},
            {'data': 'cargo'},
            {'data': 'groups__name'},
            {'data': 'email'},
            {'data': 'is_active'},
            {'data': 'id'}
        ],
        columnDefs: [
            {
                targets: [1, 2, 4],
                class: 'td-actions text-center'
            },
            {
                targets: [0],
                className: 'td-actions text-center',
                render: function (data, type, row) {
                    return row['first_name'] + ' ' + row['last_name'];
                }
            },
            {
                targets: [3],
                class: 'td-actions text-center',
                render: function (data, type, row) {
                    return '<span class="badge badge-pill badge-primary">' + row['groups__name'] + '</span>'
                }
            },
            {
                targets: [5],
                className: 'td-actions text-center',
                render: function (data, type, row) {
                    let estado = null;
                    switch (row['is_active']) {
                        case true:
                            estado = 'Activo'
                            break;
                        case false:
                            estado = 'Inactivo'
                            break;
                    }
                    return estado;
                }
            },
            {
                targets: [6],
                class: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    let actions
                    actions = '<a href="/user/detail/' + row['slug'] + '/" type="button" rel="tooltip" class="btn btn-info btn-link btn-icon btn-sm" title="Detalle Perfil"><i class="nc-icon nc-tv-2"></i></a>&nbsp';
                    actions += '<a href="/user/update-password/' + row['slug'] + '/" type="button" rel="tooltip" class="btn btn-success btn-link btn-icon btn-sm" title="Resetear Contraseña"><i class="nc-icon nc-key-25"></i></a>';
                    return actions
                }
            },
        ],
        initComplete: function (settings, json) {
        }
    });
});