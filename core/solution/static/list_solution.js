// Asegurarse de que jQuery esté definido antes de usar $
document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        var table = $('#data').DataTable({
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
                data: function (d) {
                    d['action'] = 'searchdata';
                    d['filter_laboratory'] = $('#id_filter_laboratory').val() || '';
                    d['filter_description'] = $('#id_filter_description').val() || '';
                    d['filter_prep_date_start'] = $('#id_filter_prep_date_start').val() || '';
                    d['filter_prep_date_end'] = $('#id_filter_prep_date_end').val() || '';
                    d['filter_expire_date_start'] = $('#id_filter_expire_date_start').val() || '';
                    d['filter_expire_date_end'] = $('#id_filter_expire_date_end').val() || '';
                    d['filter_quantity_min'] = $('#id_filter_quantity_min').val() || '';
                    d['filter_quantity_max'] = $('#id_filter_quantity_max').val() || '';
                    d['filter_prepared_by'] = $('#id_filter_prepared_by').val() || '';
                },
                dataSrc: ""
            },
            columns: [
                {'data': 'code_solution'},
                {'data': 'solute_reagent__reagent__description_reagent'},
                {'data': 'concentration'},
                {'data': 'preparation_date'},
                {'data': 'expire_date_solution'},
                {'data': 'quantity_available_sln'},
                {'data': 'preparated_by__get_full_name'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1],
                    class: 'td-actions text-center'
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['preparation_date'] === null || row['preparation_date'] === undefined) {
                            return '<span class="badge bg-secondary">Pendiente</span>';
                        } else {
                            return row['preparation_date'];
                        }
                    }
                },
                {
                    targets: [6],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['preparated_by'] === null || row['preparated_by'] === undefined) {
                            return '<span class="badge bg-secondary">Pendiente</span>';
                        } else {
                            return row['preparated_by__get_full_name'];
                        }
                    }
                },
                {
                    targets: [2],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['concentration'] + ' ' + row['concentration_unit'];
                    }
                },
                {
                    targets: [5],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['quantity_available_sln'] === null || row['quantity_available_sln'] === undefined) {
                            return '<span class="badge bg-secondary">Sin Confirmar</span>';
                        } else {
                            return row['quantity_available_sln'];
                        }
                    }
                },
                {
                    targets: [4],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let expireDate = row['expire_date_solution'];

                        // Verificar si la fecha es null o undefined
                        if (expireDate === null || expireDate === undefined) {
                            return '<span class="badge bg-secondary">Sin fecha</span>';
                        }

                        // Comparar con la fecha actual
                        if (expireDate < toDay) {
                            return '<span class="badge bg-danger">' + expireDate + '</span>';
                        } else {
                            return expireDate;
                        }
                    }
                },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/solution/detail/' + row['id'] + '/" type="button" title="Detalle de Preparación"><i class="bi bi-info-square text-info"></i></a> &nbsp';
                        if (row['preparation_confirmed'] === false){
                            actions += '<a href="/solution/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        }
                        return actions
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });

        $('.filter-control').on('change', function () {
            table.ajax.reload();
        });

        $('#id_filter_description').on('keyup', function () {
            table.ajax.reload();
        });

        $('#btn_clear_filters').on('click', function () {
            $('.filter-control').val('');
            table.ajax.reload();
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});
