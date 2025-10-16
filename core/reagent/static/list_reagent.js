// Asegurarse de que jQuery esté definido antes de usar $
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
                {'data': 'code_reagent'},
                {'data': 'description_reagent'},
                {'data': 'umb'},
                {'data': 'manufacturer'},
                {'data': 'site__site_name'},
                {'data': 'enable_reagent'},
                {'data': 'technical_sheet'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3, 4],
                    class: 'td-actions text-center'
                },
                {
                    targets: [5],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['enable_reagent']) {
                            case true:
                                return '<span class="badge bg-primary rounded-pill">' + 'Activo' + '</span>';
                                break;
                            case false:
                                return '<span class="badge badge-sm badge-danger">' + 'Inactivo' + '</span>';
                                break;
                        }
                        return estado;
                    }
                },
                {
                    targets: [6],
                    className: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a title="Descargar" target="_blank" class="bi bi-file-earmark-pdf text-danger" href="/reagent/technical_sheet/?id=' + row.id + '&type=technical_sheet">';
                    }
                },
                {
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/reagent/detail/' + row['id'] + '/" type="button" title="Detalle Perfil"><i class="bi bi-info-square text-info"></i></a> &nbsp';
                        actions += '<a href="/reagent/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions
                    }
                },
            ],
            initComplete: function (settings, json) {
                console.log("DataTable inicializada correctamente");
            }
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});