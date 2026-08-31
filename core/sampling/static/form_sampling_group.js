(function() {
    var done = false;

    function calc($s, $i) {
        var id = $s.val();
        if (!id) { $i.val(''); return; }
        axios.get('/sampling/api/sampling-point/' + id + '/')
            .then(function(r) {
                if (r.data && r.data.sample_frequency) {
                    var f = parseInt(r.data.sample_frequency);
                    $i.val(f > 0 ? Math.floor(24 / f) : '');
                } else {
                    $i.val('');
                }
            })
            .catch(function() { $i.val(''); });
    }

    function init() {
        if (done) return;
        var $s = $('select[name="sampling_point"]');
        var $i = $('input[name="number_sampling_day"]');
        if (!$s.length || !$i.length) return;
        done = true;

        $i.prop('readonly', true);

        $s.on('select2:select', function() {
            calc($s, $i);
        });

        if ($s.val()) {
            calc($s, $i);
        }
    }

    $(document).on('modal:loaded', init);

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();