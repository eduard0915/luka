document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 3, "desc" ]],
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
                {'data': 'group_sampling'},
                {'data': 'number_sample'},
                {'data': 'date_sampling_scheduled'},
                {'data': 'date_sampling'},
                {'data': 'status_sampling'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1],
                    class: 'td-actions text-start'
                },
                {
                    targets: [2, 3, 4],
                    class: 'td-actions text-center'
                },
                {
                    targets: [-1],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/sampling/process/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/sampling/process/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                }
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
