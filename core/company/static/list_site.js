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
            {'data': 'site_name'},
            {'data': 'site_address'},
            {'data': 'site_city'},
            {'data': 'site_country'},
            {'data': 'site_enable'},
            {'data': 'id'}
        ],
        columnDefs: [
            {
                targets: [0, 1, 2, 3],
                class: 'td-actions text-center'
            },
            {
                targets: [4],
                className: 'td-actions text-center',
                render: function (data, type, row) {
                    let estado = null;
                    switch (row['site_enable']) {
                        case true:
                            return '<span class="badge badge-sm badge-success">' + 'Activo' + '</span>';
                            break;
                        case false:
                            return '<span class="badge badge-sm badge-danger">' + 'Inactivo' + '</span>';
                            break;
                    }
                    return estado;
                }
            },
            {
                targets: [5],
                class: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    let actions
                    actions = '<a href="/company/detail/' + row['id'] + '/" type="button" title="Inactivar"><i class="fa-solid fa-power-off text-info"></i></a> &nbsp';
                    actions += '<a href="/company/update_site/' + row['id'] + '/" type="button" title="Editar"><i class="fa-solid fa-edit text-warning"></i></a> &nbsp';
                    return actions
                }
            },
        ],
        initComplete: function (settings, json) {
        }
    });
});