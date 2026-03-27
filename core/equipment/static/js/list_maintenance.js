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
                {'data': 'equipment_instrumental__code_equipment'},
                {'data': 'date_maintenance'},
                {'data': 'type_maintenance'},
                {'data': 'maintenance_by'},
                {'data': 'responsible_user__full_name'},
                {'data': 'has_file'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'td-actions text-center'
                },
                {
                    targets: [1, 2, 3, 4],
                    class: 'td-actions text-start'
                },
                {
                    targets: [5],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (data) {
                            return '<i class="bi bi-file-earmark-check-fill text-success" title="Tiene archivo adjunto"></i>';
                        }
                        return '<i class="bi bi-file-earmark-x text-muted" title="Sin archivo adjunto"></i>';
                    }
                },
                {
                    targets: [-1],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/equipment/maintenance/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/equipment/maintenance/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
