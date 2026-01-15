// Asegurarse de que jQuery esté definido antes de usar $
document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
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
                data: {
                    'action': 'searchdata'
                },
                dataSrc: ""
            },
            columns: [
                {'data': 'sampling_point'},
                {'data': 'first_hour_sampling'},
                {'data': 'number_sampling_day'},
                {'data': 'enable_sampling_group'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'td-actions text-start'
                },
                {
                    targets: [1, 2],
                    class: 'td-actions text-center'
                },
                {
                    targets: [4],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/sampling/group/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/sampling/group/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        if (row['enable_sampling_group']) {
                            return '<span class="badge bg-success">Sí</span>';
                        } else {
                            return '<span class="badge bg-danger">No</span>';
                        }
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});