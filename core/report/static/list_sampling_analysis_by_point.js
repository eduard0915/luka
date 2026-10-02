var tblAnalysis;
var select_sample_point;

function showLoading() {
    $('#table_loading').removeClass('d-none');
    $('#data').closest('.table-responsive').addClass('d-none');
}

function hideLoading() {
    $('#table_loading').addClass('d-none');
    $('#data').closest('.table-responsive').removeClass('d-none');
}

function initTable(json) {
    var container = $('#data').closest('.table-responsive');
    if (!container.length) {
        container = $('.table-responsive').first();
    }

    // Destruye la instancia previa y elimina la tabla para evitar que DataTables
    // conserve referencias al thead/tbody reconstruidos entre cargas.
    if ($.fn.DataTable.isDataTable('#data')) {
        try {
            $('#data').DataTable().destroy(true);
        } catch (e) {
            // La tabla pudo quedar en un estado inconsistente por una carga previa
        }
    }
    $('#data_wrapper').remove();
    $('#data').remove();

    var headerHtml = '';
    var columns = [];
    if (json.columns && json.columns.length) {
        var headers = ['Fecha y Hora'];
        columns.push({"data": "date_analysis"});
        json.columns.forEach(function (col) {
            headers.push(col);
            columns.push({"data": col});
        });
        headers.forEach(function (header) {
            headerHtml += '<th>' + header + '</th>';
        });
    }

    // Sin columnas de datos: la tabla queda en blanco
    if (!columns.length) {
        container.append('<table class="table table-hover table-bordered" id="data"></table>');
        return;
    }

    var table = $(
        '<table class="table table-hover table-bordered" id="data">' +
        '<thead><tr>' + headerHtml + '</tr></thead><tbody></tbody></table>'
    );
    container.append(table);

    tblAnalysis = table.DataTable({
        responsive: {
            details: false
        },
        autoWidth: false,
        deferRender: true,
        data: json.data,
        columns: columns,
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

function loadData() {
    var product = $('#id_product').val();
    var sample_point = $('#id_sample_point').val();
    var start_date = $('#id_start_date').val();
    var end_date = $('#id_end_date').val();

    if (!sample_point) {
        initTable({columns: [], data: []});
        hideLoading();
        return false;
    }

    showLoading();
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'searchdata',
            'product': product,
            'sample_point': sample_point,
            'start_date': start_date,
            'end_date': end_date
        },
        dataType: 'json',
    }).done(function (json) {
        if (!json.hasOwnProperty('error')) {
            initTable(json);
            return false;
        }
        message_error(json.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function () {
        hideLoading();
    });
}

$(function () {
    select_sample_point = $('#id_sample_point');

    $('#id_product').on('change', function () {
        var id = $(this).val();
        var options = '<option value="">---------</option>';
        initTable({columns: [], data: []});
        if (id === '') {
            select_sample_point.html(options);
            hideLoading();
            return false;
        }
        showLoading();
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'search_sample_point',
                'id': id
            },
            dataType: 'json',
        }).done(function (data) {
            if (!data.hasOwnProperty('error')) {
                $.each(data, function (key, value) {
                    options += '<option value="' + value.id + '">' + value.text + '</option>';
                });
                return false;
            }
            message_error(data.error);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(textStatus + ': ' + errorThrown);
        }).always(function () {
            select_sample_point.html(options);
            hideLoading();
            loadData();
        });
    });

    $('#id_sample_point').on('change', function () {
        loadData();
    });

    $('#id_start_date, #id_end_date').on('change changeDate', function () {
        loadData();
    });

    $('.btnExcel').on('click', function () {
        var product = $('#id_product').val();
        var sample_point = $('#id_sample_point').val();
        var start_date = $('#id_start_date').val();
        var end_date = $('#id_end_date').val();

        if (!sample_point) {
            alert('Debe seleccionar un punto de muestreo');
            return false;
        }

        var url = window.location.pathname + 'excel/?product=' + product + '&sample_point=' + sample_point + '&start_date=' + start_date + '&end_date=' + end_date;
        window.open(url, '_blank');
    });

    // Carga inicial: tabla en blanco
    initTable({columns: [], data: []});
});
