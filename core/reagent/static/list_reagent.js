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
            {'data': 'code_reagent'},
            {'data': 'description_reagent'},
            {'data': 'enable_reagent'},
            {'data': 'manufacturer'},
            {'data': 'technical_sheet'},
            {'data': 'id'}
        ],
        columnDefs: [
            {
                targets: [0, 1, 3],
                class: 'td-actions text-center'
            },
            {
                targets: [2],
                className: 'td-actions text-center',
                render: function (data, type, row) {
                    let estado = null;
                    switch (row['enable_reagent']) {
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
                targets: [4],
                className: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<a title="Descargar" target="_blank" style="color:red" class="fa fa-file-pdf" href="/reagent/technical_sheet?id=' + row.id + '&type=technical_sheet">';

                }
            },
            {
                targets: [5],
                class: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    let actions
                    actions = '<a href="/reagent/detail/' + row['id'] + '/" type="button" title="Detalle Perfil"><i class="fa-solid fa-power-off text-info ml-2"></i></a> &nbsp&nbsp';
                    actions += '<a href="/reagent/update/' + row['id'] + '/" type="button" title="Editar"><i class="fa-solid fa-edit text-warning"></i></a> &nbsp';
                    return actions
                }
            },
        ],
        initComplete: function (settings, json) {
        }
    });
});