var tblAnalysis;

$(function () {
    tblAnalysis = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
        columns: [
            {"data": "sampling_process.number_sample"},
            {"data": "sampling_process.sampling_point"},
            {"data": "analytical_method"},
            {"data": "average_concentration"},
            {"data": "date_analysis"},
            {"data": "id"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '<a href="/sampling/analysis/detail/' + row.id + '/" class="btn btn-info btn-sm btn-flat"><i class="fas fa-search"></i></a> ';
                    buttons += '<a rel="delete" class="btn btn-danger btn-sm btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });

    $('#data tbody').on('click', 'a[rel="delete"]', function () {
        var tr = tblAnalysis.cell($(this).closest('td, li')).index();
        var data = tblAnalysis.row(tr.row).data();
        var parameters = new FormData();
        parameters.append('action', 'delete');
        parameters.append('id', data.id);
        submit_with_ajax(window.location.pathname.replace('list', 'delete') + data.id + '/', 'Notificación', '¿Estas seguro de eliminar el registro?', parameters, function () {
            tblAnalysis.ajax.reload();
        });
    });
});
