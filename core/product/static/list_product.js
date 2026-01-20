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
                {"data": "code_product"},
                {"data": "description_product"},
                {"data": "version"},
                {"data": "enable_product"},
                {"data": "id"},
            ],
            columnDefs: [
                {
                    targets: [4],
                    class: 'td-actions text-center align-middle',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '<a href="/product/detail/' + row.id + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info m-0"></i></a> &nbsp;';
                        actions += '<a href="/product/update/' + row.id + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning m-0"></i></a>';
                        return actions;
                    }
                },
                {
                    targets: [3],
                    class: 'td-actions text-center align-middle',
                    render: function (data, type, row) {
                        if (data) {
                            return '<span class="badge bg-success">Sí</span>';
                        }
                        return '<span class="badge bg-danger">No</span>';
                    }
                },
                {
                    targets: [0, 1, 2],
                    class: 'td-actions text-center align-middle',
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});