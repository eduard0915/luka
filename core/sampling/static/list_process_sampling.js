document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 2, "desc" ]],
            language: {
                url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
            },
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: function (d) {
                    d.action = 'searchdata';
                    d.status_filter = typeof status_filter !== 'undefined' ? status_filter : '';
                },
                dataSrc: ""
            },
            columns: [
                {'data': 'group_sampling'},
                {'data': 'number_sample'},
                {'data': 'date_sampling_scheduled'},
                {'data': 'sampling_created_by__get_full_name'},
                {'data': 'status_sampling'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'td-actions text-start align-middle',
                    render: function (data, type, row) {
                        if (row['group_sampling'] === 'None' || row['group_sampling'] === '' || row['group_sampling'] === undefined || row['group_sampling'] === null) {
                            return row['point_sampling'];
                        } else {
                            return row['group_sampling'];
                        }
                    }
                },
                {
                    targets: [4],
                    class: 'td-actions text-center align-middle',
                    render: function (data, type, row) {
                        let status = data;
                        let badge_class = 'bg-secondary';
                        let text_class = '';

                        if (status === 'Programada') {
                            badge_class = 'bg-warning';
                            text_class = 'text-dark';
                        } else if (status === 'Confirmada') {
                            badge_class = 'bg-info';
                        } else if (status === 'En Proceso') {
                            badge_class = 'bg-primary';
                        } else if (status === 'Procesada') {
                            badge_class = 'bg-success';
                        } else if (status === 'Cancelada') {
                            badge_class = 'bg-secondary';
                        }

                        return '<span class="badge ' + badge_class + ' ' + text_class + '">' + status + '</span>';
                    }
                },
                {
                    targets: [1, 2, 3],
                    class: 'td-actions text-center align-middle'
                },
                {
                    targets: [5],
                    class: 'td-actions text-center align-middle',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/sampling/process/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a>  &nbsp;';
                        if (row['status_sampling'] === 'Programada') {
                            actions += '<a href="/sampling/process/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>  &nbsp;';
                            actions += '<a onclick=open_modal("/sampling/process/confirmed/' + row['id'] + '/") type="button" title="Confirmar Muestra"><i class="bi bi-check-square text-success"></i></a>';
                        }
                        return actions;
                    }
                }
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
