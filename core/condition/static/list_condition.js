document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
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
                {'data': 'laboratory'},
                {'data': 'area'},
                {'data': 'variable'},
                {'data': 'upper_limit'},
                {'data': 'lower_limit'},
                {'data': 'enabled'},
                {'data': 'id'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2],
                    class: 'td-actions text-center align-middle'
                },
                {
                    targets: [3, 4, 5],
                    class: 'td-actions text-center align-middle'
                },
                {
                    targets: [5],
                    render: function (data, type, row) {
                        if (row['enabled'] === 'Sí') {
                            return '<span class="badge bg-success">Sí</span>';
                        } else {
                            return '<span class="badge bg-danger">No</span>';
                        }
                    }
                },
                {
                    targets: [6],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        let actions = '';
                        actions += '<a href="/condition/update/' + row['id'] + '/" title="Editar" class="me-1"><i class="bi bi-pencil-square text-warning"></i></a> &nbsp';
                        actions += '<a rel="graph" title="Gráfica Últimos 12 Registros" class="text-primary" style="cursor: pointer;"><i class="bi bi-graph-up"></i></a>';
                        return actions;
                    }
                },
            ],
            initComplete: function (settings, json) {
            }
        });

        $('#data tbody').on('click', 'a[rel="graph"]', function () {
            let tr = $(this).closest('tr');
            let data = $('#data').DataTable().row(tr).data();
            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_graph',
                    'id': data.id
                },
                dataType: 'json',
            }).done(function (response) {
                if (!response.hasOwnProperty('error')) {
                    $('#myModalGraph').modal('show');
                    // Actualizar el título del modal dinámicamente
                    $('#exampleModalLabel').html('<i class="bi bi-graph-up me-2"></i> Comportamiento de "' + data.variable + '" del área "' + data.area + '"');
                    renderChart(response, data.variable, data.area);
                } else {
                    alert(response.error);
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(textStatus + ': ' + errorThrown);
            });
        });
    }

    let chart;

    function renderChart(data, variable, area) {
        const ctx = document.getElementById('myChart');
        if (chart) {
            chart.destroy();
        }

        // Calcular el máximo y el mínimo para ajustar la escala del eje Y
        const allValues = [
            ...data.map(i => i.data),
            ...data.map(i => i.upper_limit),
            ...data.map(i => i.lower_limit)
        ];
        const maxVal = Math.max(...allValues);
        const minVal = Math.min(...allValues);

        // Max con 15% adicional al rango superior
        let chartMax = maxVal + (maxVal * 0.15);
        let chartMin = minVal;

        // Si el límite inferior es diferente de cero, aplicar lo mismo (15% menos al rango inferior)
        if (minVal !== 0) {
            chartMin = minVal - (minVal * 0.15);
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(i => i.date),
                datasets: [
                    {
                        label: 'Dato Registrado',
                        data: data.map(i => i.data),
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 5,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Límite Superior',
                        data: data.map(i => i.upper_limit),
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: false
                    },
                    {
                        label: 'Límite Inferior',
                        data: data.map(i => i.lower_limit),
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgb(54, 162, 235)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Comportamiento de "' + variable + '" del área "' + area + '"'
                    },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: chartMin,
                        max: chartMax
                    }
                }
            }
        });
    }
});
