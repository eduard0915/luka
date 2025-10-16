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
                {'data': 'first_name'},
                {'data': 'username'},
                {'data': 'cargo'},
                {'data': 'groups__name'},
                {'data': 'email'},
                {'data': 'site__site_name'},
                {'data': 'is_active'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [1, 2, 4, 5],
                    class: 'td-actions text-center'
                },
                {
                    targets: [0],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        return row['first_name'] + ' ' + row['last_name'];
                    }
                },
                {
                    targets: [3],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return '<span class="text-primary">' + row['groups__name'] + '</span>'
                    }
                },
                {
                    targets: [6],
                    className: 'td-actions text-center',
                    render: function (data, type, row) {
                        let estado = null;
                        switch (row['is_active']) {
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
                    targets: [7],
                    class: 'td-actions text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions
                        actions = '<a href="/user/detail/' + row['slug'] + '/" type="button" title="Detalle Perfil"><i class="bi bi-info-square text-info"></i></a> &nbsp';
                        actions += '<a href="/user/update-admin/' + row['slug'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a> &nbsp';
                        actions += '<a href="/user/update-password/' + row['slug'] + '/" type="button" title="Resetear Contraseña"><i class="bi bi-lock text-success"></i></a>';
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