var tblProcessing;

$(function () {
    tblProcessing = $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            }
        },
        columns: [
            {"data": "analyzed_by", "orderable": true},
            {"data": "analyzed_date", "orderable": true},
            {"data": "sample_analysis.analytical_method", "orderable": true},
            {"data": "concentration_sample_display", "orderable": true},
            {"data": "sample_analysis.sampling_process.number_sample", "orderable": true}
        ],
        columnDefs: [
            {
                targets: ['_all'],
                class: 'text-center',
            },
        ],
    });
});
