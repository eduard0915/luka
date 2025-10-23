// Asegurarse de que jQuery esté definido antes de usar $
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
                {'data': 'code_solution'},
                {'data': 'solute_reagent__reagent__description_reagent'},
                {'data': 'concentration'},
                {'data': 'preparation_date'},
                {'data': 'expire_date_solution'},
                {'data': 'quantity_solution'},
                {'data': 'preparated_by__get_full_name'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3, 4, 5, 6],
                    class: 'td-actions text-center'
                },
                {
                    targets: [2],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['concentration'] + ' ' + row['concentration_unit'];
                    }
                },
                // {
                //     targets: [6],
                //     className: 'td-actions text-center',
                //     render: function (data, type, row) {
                //         let estado = null;
                //         switch (row['enable_reagent']) {
                //             case true:
                //                 return '<span class="badge bg-primary rounded-pill">' + 'Activo' + '</span>';
                //                 break;
                //             case false:
                //                 return '<span class="badge badge-sm badge-danger">' + 'Inactivo' + '</span>';
                //                 break;
                //         }
                //         return estado;
                //     }
                // },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/solution/detail/' + row['id'] + '/" type="button" title="Detalle de Preparación"><i class="bi bi-info-square text-info"></i></a> &nbsp';
                        actions += '<a href="/solution/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions
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