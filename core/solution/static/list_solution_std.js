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
                {'data': 'code_solution_std'},
                {'data': 'solute_std__reagent__description_reagent'},
                {'data': 'concentration_std'},
                {'data': 'preparation_std_date'},
                {'data': 'expire_std_date_solution'},
                {'data': 'quantity_solution_std'},
                {'data': 'preparated_std_by__get_full_name'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 5],
                    class: 'td-actions text-center'
                },
                {
                    targets: [2],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['concentration_std'] + ' ' + row['concentration_unit'];
                    }
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['preparation_std_date'] === null || row['preparation_std_date'] === undefined) {
                            return '<span class="badge bg-secondary">No aplica</span>';
                        } else {
                            return row['preparation_std_date'];
                        }
                    }
                },
                {
                    targets: [4],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let expireDate = row['expire_std_date_solution'];

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
                    targets: [6],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['preparated_std_by'] === null || row['preparated_std_by'] === undefined) {
                            return row['solute_std__reagent__manufacturer'];
                        } else {
                            return row['preparated_std_by__get_full_name'];
                        }
                    }
                },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/solution/detail_std/' + row['id'] + '/" type="button" title="Detalle de Preparación"><i class="bi bi-info-square text-info"></i></a> &nbsp';
                        // actions += '<a href="/solution/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
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
