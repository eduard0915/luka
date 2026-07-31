var tblMassiveAnalysis;

$(function () {
    tblMassiveAnalysis = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        searching: false,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: function (d) {
                d.action = 'searchdata';
                d.start_date = $('#id_start_date').val();
                d.end_date = $('#id_end_date').val();
                d.analized_by = $('#id_analized_by').val();
                d.analytical_method = $('#id_analytical_method').val();
                d.sample = $('#id_sample').val();
            }
        },
        columns: [
            {"data": "sampling_process", "orderable": true},
            {"data": "product", "orderable": false},
            {"data": "analytical_method", "orderable": true},
            {"data": "metal", "orderable": true},
            {"data": "result", "orderable": true},
            {"data": "date_analysis", "orderable": true},
            {"data": "analized_by", "orderable": true}
        ],
        columnDefs: [
            {
                targets: ['_all'],
                class: 'text-center',
                defaultContent: '-'
            },
        ],
        order: [[5, 'desc']],
        language: {
            url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
        }
    });

    $('#id_start_date, #id_end_date, #id_analized_by, #id_analytical_method').on('change', function () {
        tblMassiveAnalysis.ajax.reload();
    });

    var searchTimeout = null;
    $('#id_sample').on('keyup', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            tblMassiveAnalysis.ajax.reload();
        }, 400);
    });
});
