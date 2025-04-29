$(document).ready(function($) {
    $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        language: {
            "emptyTable": "No hay información",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ Registros",
            "infoEmpty": "Mostrando 0 to 0 of 0 Registros",
            "infoFiltered": "(Filtrado de _MAX_ total Registros)",
            "lengthMenu": "Mostrar _MENU_ Registros",
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "search": "Buscar:",
            "zeroRecords": "Sin resultados encontrados",
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
                    return '<span class="badge bg-gradient-info">' + row['groups__name'] + '</span>'
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
                    actions = '<a href="/user/detail/' + row['slug'] + '/" type="button" title="Detalle Perfil"><i class="fa-solid fa-user-check text-warning"></i></a>  &nbsp';
                    actions += '<a href="/user/update-password/' + row['slug'] + '/" type="button" title="Resetear Contraseña"><i class="fa-solid fa-lock text-success"></i></a>';
                    return actions
                }
            },
        ],
        initComplete: function (settings, json) {
        }
    });
});