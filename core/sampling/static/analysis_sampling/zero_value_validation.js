/**
 * zero_value_validation.js
 *
 * Valida en el modal de "Cálculo Relacional" los campos numerator y
 * denominator:
 *  - Si alguno de los dos está en cero, se muestra "Valores en Cero"
 *    (alert-danger) y se bloquea el envío del formulario.
 *  - Si ambos valores son distintos de cero, se muestra el mensaje de
 *    confirmación "¿Está Seguro de Ejecutar el Calculo?" (alert-warning)
 *    y se permite el envío.
 */

$(function () {

    var $form = $('#modal_form');
    var $numerator = $('#id_numerator');
    var $denominator = $('#id_denominator');
    var $submitBtn = $('#btnSubmit');

    if ($numerator.length === 0 || $denominator.length === 0) {
        return;
    }

    // Contenedor del mensaje "Valores en Cero" (se crea una sola vez)
    var $zeroBox = $(
        '<div class="alert alert-danger text-center zero-value-alert" style="display:none;">' +
        '<i class="bi bi-exclamation-triangle-fill me-2"></i>Valores en Cero, verifique los resultados de los análisis relacionados' +
        '</div>'
    );

    // Contenedor del mensaje de confirmación (se crea una sola vez)
    var $confirmBox = $(
        '<div class="alert alert-warning text-center confirm-calculo-alert" style="display:none;">' +
        '<i class="bi bi-exclamation-triangle-fill me-2"></i>¿Está Seguro de Ejecutar el Calculo?' +
        '</div>'
    );

    $form.find('.modal-body').prepend($confirmBox);
    $form.find('.modal-body').prepend($zeroBox);

    function isZero(value) {
        var num = parseFloat(value);
        return isNaN(num) || num === 0;
    }

    function hasZeroValues() {
        return isZero($numerator.val()) || isZero($denominator.val());
    }

    function toggleWarning() {
        if (hasZeroValues()) {
            $zeroBox.show();
            $confirmBox.hide();
            $submitBtn.prop('disabled', true);
            return true;
        } else {
            $zeroBox.hide();
            $confirmBox.show();
            $submitBtn.prop('disabled', false);
            return false;
        }
    }

    // Validar al cargar el modal y cada vez que cambien los valores
    toggleWarning();
    $numerator.on('input change', toggleWarning);
    $denominator.on('input change', toggleWarning);

    // Validación adicional al intentar enviar el formulario, por si los
    // valores fueron modificados mediante scripts o de forma programática
    $form.on('submit', function (e) {
        if (hasZeroValues()) {
            e.preventDefault();
            e.stopImmediatePropagation();
            $submitBtn.prop('disabled', false).html(
                $submitBtn.data('original-text') || 'Si, Ejecutar'
            );
            toggleWarning();
            return false;
        }
    });

    // Guardar el texto original del botón para poder restaurarlo si se bloquea el envío
    $submitBtn.data('original-text', $submitBtn.html());

});