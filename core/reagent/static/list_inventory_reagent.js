document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
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
                {'data': 'reagent__code_reagent'},
                {'data': 'reagent__description_reagent'},
                {'data': 'purity'},
                {'data': 'batch_number'},
                {'data': 'certificate_quality'},
                {'data': 'date_expire'},
                {'data': 'quantity_stock'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 3, 5],
                    class: 'td-actions text-center'
                },
                {
                    targets: [2],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['purity'] + ' ' + row['reagent__purity_unit'];
                    }
                },
                {
                    targets: [4],
                    className: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a title="Descargar Certificado de Calidad" target="_blank" class="bi bi-file-earmark-pdf text-danger" href="transaction_reagent/coa/?id=' + row.id + '&type=certificate_quality"></a>';
                    }
                },
                {
                    targets: [6],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['quantity_stock'] + ' ' + row['reagent__umb'];
                    }
                },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/reagent/inventory/detail/' + row['id'] + '/" type="button" title="Detalle de Movimientos"><i class="bi bi-info-square text-info"></i></a>&nbsp';
                        actions += '<a href="/reagent/inventory/update/' + row['id'] + '/" type="button" title="Editar Entrada"><i class="bi bi-pencil-square text-warning"></i></a>&nbsp';
                        actions += '<a onclick=open_modal("/reagent/inventory/delete/' + row['id'] + '/") type="button" title="Eliminar Entrada"><i class="bi bi-trash text-danger"></i></a>&nbsp';
                        actions += '<a href="/reagent/transaction_reagent/add/' + row['id'] + '/" type="button" title="Registrar Movimiento"><i class="bi bi-bag-plus text-primary"></i></a>';
                        return actions
                    }
                },
            ],
            "createdRow": function (row, data, dataIndex) {
                if (data.date_expire < toDay) {
                    $('td:eq(5)', row).css('background-color', '#FF0000').css('color', 'white').css('width', '10%');
                }
            },
            initComplete: function (settings, json) {
            },
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});