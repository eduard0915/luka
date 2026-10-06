// Asegurarse de que jQuery esté definido antes de usar $
document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 0, "asc" ]],
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
                {'data': 'laboratory_name'},
                {'data': 'site__site_name'},
                {'data': 'process'},
                {'data': 'enable_laboratory'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2],
                    class: 'td-actions text-start'
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['enable_laboratory']) {
                            return '<span class="badge bg-success">Sí</span>';
                        } else {
                            return '<span class="badge bg-danger">No</span>';
                        }
                    }
                },
                {
                    targets: [4],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a href="/laboratory/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});