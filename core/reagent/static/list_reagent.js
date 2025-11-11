// Asegurarse de que jQuery esté definido antes de usar $
document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            order: [[ 0, "desc" ]],
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
                {'data': 'purity_unit'},
                {'data': 'manufacturer'},
                {'data': 'enable_reagent'},
                {'data': 'technical_sheet'},
                {'data': 'stability_solution'},
                {'data': 'volumetric'},
                {'data': 'solvent'},
                {'data': 'density_enable'},
                {'data': 'standard'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2, 3, 4, 5, 7],
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
                    targets: [8],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['volumetric']) {
                            case true:
                                return 'Si';
                                break;
                            case false:
                                return 'No';
                                break;
                        }
                        return estado;
                    }
                },
                {
                    targets: [9],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['solvent']) {
                            case true:
                                return 'Si';
                                break;
                            case false:
                                return 'No';
                                break;
                        }
                        return estado;
                    }
                },
                {
                    targets: [10],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['density_enable']) {
                            case true:
                                return 'Si';
                                break;
                            case false:
                                return 'No';
                                break;
                        }
                        return estado;
                    }
                },
                {
                    targets: [11],
                    className: 'text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['standard']) {
                            case true:
                                return 'Si';
                                break;
                            case false:
                                return 'No';
                                break;
                        }
                        return estado;
                    }
                },
                // {
                //     targets: [12],
                //     class: 'td-actions text-center',
                //     orderable: false,
                //     render: function (data, type, row) {
                //         let actions
                //         actions = '<a href="/reagent/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>&nbsp';
                //         if (row['standard'] === false && row['solvent'] === false) {
                //             actions += '<a onclick=open_modal("/solution/add_standardization/' + row['id'] + '/") type="button" title="Estandarización"><i class="bi bi-award-fill text-info"></i></a>';
                //         }
                //         return actions;
                //     }
                // },
                {
                    targets: [12],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';

                        // Botón de editar reactivo
                        actions += '<a href="/reagent/update/' + row['id'] + '/" type="button" title="Editar">';
                        actions += '<i class="bi bi-pencil-square text-warning"></i></a>&nbsp;';

                        // Validar si puede tener estandarización
                        if (row['standard'] === false && row['solvent'] === false) {

                            // Si NO tiene estandarización: mostrar botón para CREAR
                            if (row['has_standardization'] === false) {
                                actions += '<a onclick="open_modal(\'/solution/add_standardization/' + row['id'] + '/\')" ';
                                actions += 'type="button" title="Agregar Estandarización">';
                                actions += '<i class="bi bi-award-fill text-info"></i></a>&nbsp;';
                            }
                            // Si YA tiene estandarización: mostrar botón para EDITAR
                            else {
                                actions += '<a onclick="open_modal(\'/solution/update_standardization/' + row['standardization_id'] + '/\')" ';
                                actions += 'type="button" title="Editar Estandarización">';
                                actions += '<i class="bi bi-award-fill text-success"></i></a>&nbsp;';
                            }
                        }

                        return actions;
                    }
                }
            ],
            initComplete: function (settings, json) {
            }
        });
    } else {
        console.error("jQuery ($ variable) no está definido. Verifica que jQuery se haya cargado correctamente.");
    }
});