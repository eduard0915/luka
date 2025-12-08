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
                {'data': 'code_analytical_method'},
                {'data': 'description_analytical_method'},
                {'data': 'laboratory__laboratory_name'},
                {'data': 'type_method'},
                {'data': 'sample_size'},
                {'data': 'sig_figs_result'},
                {'data': 'enable_analytical_method'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3],
                    class: 'td-actions text-start'
                },
                {
                    targets: [4, 5],
                    class: 'td-actions text-center'
                },
                {
                    targets: [6],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (row['enable_analytical_method']) {
                            return '<span class="badge bg-success">Sí</span>';
                        } else {
                            return '<span class="badge bg-danger">No</span>';
                        }
                    }
                },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/analytical_method/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/analytical_method/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});
