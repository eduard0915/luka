var tblProcessing;

$(function () {
    tblProcessing = $('#data').DataTable({
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
            {"data": "analyzed_by"},
            {"data": "analyzed_date"},
            {"data": "concentration_sample_display"},
            {"data": "sample_analysis.sampling_process.number_sample"},
            {"data": "sample_analysis.analytical_method"},
        ],
        columnDefs: [
            {
                targets: ['_all'],
                class: 'text-center',
            },
        ],
        initComplete: function (settings, json) {

        }
    });
});
