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
            {'data': 'reagent__code_reagent'},
            {'data': 'reagent__description_reagent'},
            {'data': 'batch_number'},
            {'data': 'date_expire'},
            {'data': 'quantity_ml'},
            {'data': 'id'}
        ],
        columnDefs: [
            {
                targets: [0, 1, 2, 3],
                class: 'td-actions text-center'
            },
            {
                targets: [4],
                class: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    return row['quantity_ml'] + ' ' + row['unit_measurement'];
                }
            },
            {
                targets: [5],
                class: 'td-actions text-center',
                orderable: false,
                render: function (data, type, row) {
                    let actions
                    actions = '<a href="/reagent/inventory/update/' + row['id'] + '/" type="button" title="Editar"><i class="fa-solid fa-edit text-warning"></i></a> &nbsp&nbsp';
                    // actions += '<a href="/reagent/detail/' + row['id'] + '/" type="button" title="Detalle Perfil"><i class="fa-solid fa-power-off text-info ml-2"></i></a> &nbsp';
                    return actions
                }
            },
        ],
        initComplete: function (settings, json) {
        }
    });
});