var tblAnalysis;
var select_sample_point;

function initTable(json) {
    var table = $('#data');
    if ($.fn.DataTable.isDataTable('#data')) {
        table.DataTable().destroy();
    }

    var thead = table.find('thead');
    thead.empty();
    var headerRow = $('<tr>').appendTo(thead);
    headerRow.append('<th>Fecha y Hora</th>');

    var columns = [{"data": "date_analysis"}];
    if (json.columns) {
        json.columns.forEach(function (col) {
            headerRow.append('<th>' + col + '</th>');
            columns.push({"data": col});
        });
    }

    tblAnalysis = table.DataTable({
        responsive: {
            details: false
        },
        autoWidth: false,
        destroy: true,
        deferRender: true,
        data: json.data,
        columns: columns,
        columnDefs: [
            {
                targets: ['_all'],
                class: 'text-center',
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
    
    if (!sample_point) {
        initTable({columns: [], data: []});
        return false;
    }
    
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            'action': 'searchdata',
            'product': product,
            'sample_point': sample_point
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
    });
}

$(function () {
    select_sample_point = $('#id_sample_point');

    $('#id_product').on('change', function () {
        var id = $(this).val();
        var options = '<option value="">---------</option>';
        if (id === '') {
            select_sample_point.html(options);
            loadData();
            return false;
        }
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
            loadData();
        });
    });

    $('#id_sample_point').on('change', function () {
        loadData();
    });

    $('.btnExcel').on('click', function () {
        var product = $('#id_product').val();
        var sample_point = $('#id_sample_point').val();
        
        if (!sample_point) {
            alert('Debe seleccionar un punto de muestreo');
            return false;
        }

        var url = window.location.pathname + 'excel/?product=' + product + '&sample_point=' + sample_point;
        window.open(url, '_blank');
    });

    // Carga inicial
    initTable({columns: [], data: []});
});
