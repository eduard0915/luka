document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[ 8, "asc" ], [ 2, "asc" ]],
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
                {'data': 'equipment'},
                {'data': 'date_calibration'},
                {'data': 'date_calibration_next'},
                {'data': 'calibrated_by'},
                {'data': 'parameter'},
                {'data': 'comply'},
                {'data': 'responsible_user__full_name'},
                {'data': 'id'},
                {'data': 'calibration_next_completed'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 3, 4, 6],
                    class: 'td-actions text-center'
                },
                {
                    targets: [2],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        return data;
                    },
                    createdCell: function (td, cellData, rowData, row, col) {
                        let today = new Date();
                        today.setHours(0, 0, 0, 0);

                        let parts = cellData.split('-');
                        let next_date = new Date(parts[0], parts[1] - 1, parts[2]);
                        next_date.setHours(0, 0, 0, 0);

                        let diffTime = next_date - today;
                        let diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

                        if (next_date < today && !rowData.calibration_next_completed) {
                            $(td).addClass('bg-danger text-white');
                        } else if (diffDays === 1 || diffDays === 2) {
                            $(td).addClass('bg-warning text-dark');
                        }
                    }
                },
                {
                    targets: [5],
                    class: 'td-actions text-center',
                    render: function (data, type, row) {
                        if (data) {
                            return '<span class="badge bg-success">Si</span>';
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
                        actions += '<a href="/equipment/calibration/detail/' + row['id'] + '/" type="button" title="Detalle"><i class="bi bi-info-square text-info"></i></a> &nbsp;';
                        actions += '<a href="/equipment/calibration/update/' + row['id'] + '/" type="button" title="Editar"><i class="bi bi-pencil-square text-warning"></i></a>';
                        return actions;
                    }
                },
                {
                    targets: [8],
                    visible: false
                }
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
