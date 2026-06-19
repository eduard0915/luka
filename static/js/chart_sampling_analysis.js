let chart;

function resetSelect(selector, disabled = false) {
    const $sel = $(selector);
    $sel.html('<option value="">---------</option>');
    disabled ? $sel.prop('disabled', true) : $sel.prop('disabled', false);
    $sel.trigger('change.select2');
}

function get_graph_data() {
    const product = $('#id_product').val();
    const method = $('#id_analytical_method').val();
    const point = $('#id_sample_point').val();
    const date_from = $('#id_date_from').val();
    const date_to = $('#id_date_to').val();

    if (!product || !method || !point) return;

    $('#chart-placeholder').hide();
    $('#chart-container').show();

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        data: {
            action: 'get_graph_data',
            product,
            analytical_method: method,
            sample_point: point,
            date_from: date_from,
            date_to: date_to,
        },
        dataType: 'json',
    }).done(function (data) {
        if (data.error) {
            message_error(data.error);
            return;
        }
        render_chart(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        message_error(textStatus + ': ' + errorThrown);
    });
}

function render_chart(data) {
    const ctx = document.getElementById('myChart');
    if (chart) {
        chart.destroy();
    }

    const palette = [
        'rgb(75,192,192)', 'rgb(255,99,132)', 'rgb(54,162,235)',
        'rgb(255,205,86)', 'rgb(153,102,255)', 'rgb(255,159,64)', 'rgb(201,203,207)'
    ];

    let datasets = data.series.map((item, i) => ({
        label: item.name,
        data: item.data,
        borderColor: palette[i % palette.length],
        backgroundColor: palette[i % palette.length] + '33',  // 20% opacidad
        fill: false,
        tension: 0.2,
        spanGaps: true,
        pointRadius: 4,
        pointHoverRadius: 6,
    }));

    if (data.specifications && data.specifications.length > 0) {
        data.specifications.forEach((spec, i) => {
            const pointInfo = spec.sample_point ? ` (${spec.sample_point})` : '';
            const unitSuffix = spec.unit_measure ? ` ${spec.unit_measure}` : '';

            if (spec.lower_limit !== null && spec.lower_limit !== undefined) {
                datasets.push({
                    label: `L. Inferior: ${spec.name}${pointInfo}`,
                    data: Array(data.categories.length).fill(spec.lower_limit),
                    borderColor: 'rgba(255, 0, 0, 0.5)',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    borderWidth: 2,
                    unit_measure: unitSuffix
                });
            }
            if (spec.upper_limit !== null && spec.upper_limit !== undefined) {
                datasets.push({
                    label: `L. Superior: ${spec.name}${pointInfo}`,
                    data: Array(data.categories.length).fill(spec.upper_limit),
                    borderColor: 'rgba(255, 0, 0, 0.5)',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    borderWidth: 2,
                    unit_measure: unitSuffix
                });
            }
        });
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {labels: data.categories, datasets},
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {mode: 'index', intersect: false},
            scales: {
                y: {
                    beginAtZero: false,
                    title: {display: true, text: 'Concentración Promedio'}
                },
                x: {
                    title: {display: true, text: 'Fecha y Hora'},
                    ticks: {maxRotation: 45, minRotation: 30}
                }
            },
            plugins: {
                legend: {position: 'top'},
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                                if (context.dataset.unit_measure) {
                                    label += context.dataset.unit_measure;
                                }
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// function render_chart(data) {
//     const ctx = document.getElementById('myChart');
//     if (chart) { chart.destroy(); }
//
//     const palette = [
//         'rgb(75,192,192)', 'rgb(255,99,132)', 'rgb(54,162,235)',
//         'rgb(255,205,86)', 'rgb(153,102,255)', 'rgb(255,159,64)', 'rgb(201,203,207)'
//     ];
//
//     let datasets = data.series.map((item, i) => ({
//         label: item.name,
//         data: item.data,
//         borderColor: palette[i % palette.length],
//         backgroundColor: palette[i % palette.length] + '33',  // 20% opacidad
//         fill: false,
//         tension: 0.2,
//         spanGaps: true,
//         pointRadius: 4,
//         pointHoverRadius: 6,
//     }));
//
//     if (data.specifications && data.specifications.length > 0) {
//         data.specifications.forEach((spec, i) => {
//             const pointInfo = spec.sample_point ? ` (${spec.sample_point})` : '';
//             const unitInfo = spec.unit_measure ? ` [${spec.unit_measure}]` : '';
//             if (spec.lower_limit !== null && spec.lower_limit !== undefined) {
//                 datasets.push({
//                     label: `L. Inferior: ${spec.name}${pointInfo}${unitInfo}`,
//                     data: Array(data.categories.length).fill(spec.lower_limit),
//                     borderColor: 'rgba(255, 0, 0, 0.5)',
//                     borderDash: [5, 5],
//                     fill: false,
//                     pointRadius: 0,
//                     borderWidth: 2
//                 });
//             }
//             if (spec.upper_limit !== null && spec.upper_limit !== undefined) {
//                 datasets.push({
//                     label: `L. Superior: ${spec.name}${pointInfo}${unitInfo}`,
//                     data: Array(data.categories.length).fill(spec.upper_limit),
//                     borderColor: 'rgba(255, 0, 0, 0.5)',
//                     borderDash: [5, 5],
//                     fill: false,
//                     pointRadius: 0,
//                     borderWidth: 2
//                 });
//             }
//         });
//     }
//
//     chart = new Chart(ctx, {
//         type: 'line',
//         data: { labels: data.categories, datasets },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             interaction: { mode: 'index', intersect: false },
//             scales: {
//                 y: {
//                     beginAtZero: false,
//                     title: { display: true, text: 'Concentración Promedio' }
//                 },
//                 x: {
//                     title: { display: true, text: 'Fecha y Hora' },
//                     ticks: { maxRotation: 45, minRotation: 30 }
//                 }
//             },
//             plugins: {
//                 legend: { position: 'top' },
//                 tooltip: { mode: 'index', intersect: false }
//             }
//         }
//     });
// }

$(function () {
    // Inicializar Select2
    $('.select2').select2({theme: 'bootstrap-5', width: '100%', language: 'es', placeholder: 'Seleccione una opción'});

    $('#id_product').on('change', function () {
        const id = $(this).val();

        // Resetear dependientes
        resetSelect('#id_analytical_method', true);
        resetSelect('#id_sample_point', true);

        // Ocultar gráfico
        $('#chart-container').hide();
        $('#chart-placeholder').show();
        if (chart) {
            chart.destroy();
            chart = null;
        }

        if (!id) return;

        // Cargar métodos analíticos
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {action: 'search_analytical_method', id},
            dataType: 'json',
        }).done(function (data) {
            if (data.error) {
                message_error(data.error);
                return;
            }
            const $sel = $('#id_analytical_method');
            $.each(data, function (_, v) {
                $sel.append(new Option(v.text, v.id, false, false));
            });
            $sel.prop('disabled', false).trigger('change.select2');
        }).fail(function (jqXHR, textStatus, errorThrown) {
            message_error(textStatus + ': ' + errorThrown);
        });

        // Cargar puntos de muestreo
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: {action: 'search_sample_point', id},
            dataType: 'json',
        }).done(function (data) {
            if (data.error) {
                message_error(data.error);
                return;
            }
            const $sel = $('#id_sample_point');
            $.each(data, function (_, v) {
                $sel.append(new Option(v.text, v.id, false, false));
            });
            $sel.prop('disabled', false).trigger('change.select2');
        }).fail(function (jqXHR, textStatus, errorThrown) {
            message_error(textStatus + ': ' + errorThrown);
        });
    });

    $('#id_analytical_method, #id_sample_point, #id_date_from, #id_date_to').on('change', function () {
        get_graph_data();
    });

    // Set default dates: last 30 days
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);

    $('#id_date_to').val(today.toISOString().split('T')[0]);
    $('#id_date_from').val(thirtyDaysAgo.toISOString().split('T')[0]);
});