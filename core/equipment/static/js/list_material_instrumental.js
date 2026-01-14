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
                {'data': 'code_instrumental'},
                {'data': 'description_instrumental'},
                {'data': 'brand_instrumental'},
                {'data': 'supplier_equipment'},
                {'data': 'responsible_user__full_name'},
                {'data': 'enable_instrumental'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'td-actions text-center'
                },
                {
                    targets: [1, 2, 3],
                    class: 'td-actions text-start'
                },
                {
                    targets: [4],
                    class: 'td-actions text-center'
                },
                {
                    targets: [5],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['enable_instrumental']) {
                            return '<span class="badge bg-success">Sí</span>';
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
                        actions += '<a href="/equipment/material/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/equipment/material/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
