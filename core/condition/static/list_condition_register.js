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
                {'data': 'registration_date'},
                {'data': 'condition__area'},
                {'data': 'condition__variable'},
                {'data': 'registered_data'},
                {'data': 'registered_by'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 4],
                    class: 'td-actions text-center align-middle'
                },
                {
                    targets: [3],
                    class: 'td-actions text-center align-middle',
                    render: function (data, type, row) {
                        let value = parseFloat(row.value);
                        let upper = parseFloat(row.condition__upper_limit);
                        let lower = parseFloat(row.condition__lower_limit);
                        if (value > upper || value < lower) {
                            return '<span class="badge badge-danger" style="background-color: red;">' + data + '</span>';
                        }
                        return data;
                    }
                },
                {
                    targets: [5],
                    class: 'td-actions text-center align-middle',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        if (row.actions_registered_by) {
                            actions += '<a href="/condition/register/detail/' + row['id'] + '/" title="Ver Acciones" class="me-2 btn-detail-modal"><i class="bi bi-eye-fill text-info"></i></a>';
                        }
                        actions += '<a href="/condition/register/update/' + row['id'] + '/" title="Editar" class="me-2"><i class="bi bi-pencil-square text-warning"></i></a>';
                        let value = parseFloat(row.value);
                        let upper = parseFloat(row.condition__upper_limit);
                        let lower = parseFloat(row.condition__lower_limit);
                        if (value > upper || value < lower) {
                            actions += '<a href="/condition/register/actions/' + row['id'] + '/" title="Acciones/Correcciones" class="btn-actions-modal"><i class="bi bi-exclamation-triangle-fill text-danger"></i></a>';
                        }
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });

        $('#data tbody').on('click', 'a.btn-actions-modal, a.btn-detail-modal', function (e) {
            e.preventDefault();
            let url = $(this).attr('href');
            $('#modal_template').load(url, function () {
                $(this).modal('show');
            });
        });
    }
});
