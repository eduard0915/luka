document.addEventListener('DOMContentLoaded', function () {
    if (typeof $ !== 'undefined') {
        $('#data').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            order: [[0, 'desc']],
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json'
            },
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'searchdata'
                },
                dataSrc: ''
            },
            columns: [
                {'data': 'use_date'},
                {'data': 'responsible_user__full_name'},
                {'data': 'sampling_analysis__sampling_process__number_sample'},
                {'data': 'sampling_analysis__analytical_method__description_analytical_method'}
            ],
            columnDefs: [
                {
                    targets: [0, 1, 2],
                    class: 'td-actions text-center'
                },
                {
                    targets: [3],
                    class: 'td-actions text-start'
                }
            ],
            initComplete: function (settings, json) {
            }
        });
    }
});
