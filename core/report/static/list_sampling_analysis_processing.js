var tblAnalysis;

function loadData() {
    if ($.fn.DataTable.isDataTable('#data')) {
        tblAnalysis.ajax.reload();
        return;
    }

    tblAnalysis = $('#data').DataTable({
        responsive: {
            details: false
        },
        autoWidth: false,
        deferRender: true,
        order: [[ 0, "desc" ]],
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: function (d) {
                d.action = 'searchdata';
                d.date_from = $('#id_date_from').val();
                d.date_to = $('#id_date_to').val();
                d.analyzed_by = $('#id_analyzed_by').val();
                d.profile = $('#id_profile').val();
            },
            dataSrc: "data"
        },
        columns: [
            {"data": "analyzed_date"},
            {"data": "sample_analysis"},
            {"data": "product"},
            {"data": "method"},
            {"data": "concentration_sample"},
            {"data": "analyzed_by"},
            {"data": "profile"},
        ],
        columnDefs: [
            {
                targets: ['_all'],
                class: 'text-center align-middle',
                defaultContent: '-'
            }
        ],
        language: {
            url: "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
        }
    });
}

$(function () {
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es',
        width: '100%'
    });

    $('#id_date_from, #id_date_to').on('change changeDate', function () {
        loadData();
    });

    $('#id_analyzed_by, #id_profile').on('change', function () {
        loadData();
    });

    $('.btnExcel').on('click', function () {
        var date_from = $('#id_date_from').val();
        var date_to = $('#id_date_to').val();
        var analyzed_by = $('#id_analyzed_by').val();
        var profile = $('#id_profile').val();
        var url = '/report/sampling/analysis/processing/excel/?date_from=' + date_from + '&date_to=' + date_to + '&analyzed_by=' + analyzed_by + '&profile=' + profile;
        window.open(url, '_blank');
    });

    loadData();
});
