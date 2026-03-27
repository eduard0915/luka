document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 1, "desc" ]],
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
                {'data': 'equipment'},
                {'data': 'date_verification_daily'},
                {'data': 'verified_by'},
                {'data': 'parameter_verified'},
                {'data': 'comply'},
                {'data': 'responsible_user__full_name'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3, 5],
                    class: 'td-actions text-center'
                },
                {
                    targets: [4],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (data) {
                            return '<span class="badge bg-success">Si</span>';
                        } else {
                            return '<span class="badge bg-danger">No</span>';
                        }
                    }
                },
                {
                    targets: [6],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/equipment/daily_verification/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/equipment/daily_verification/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
