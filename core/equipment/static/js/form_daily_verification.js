// ========== CARGA DINÁMICA DE REFERENCE PATTERN Y PARAMETER_VERIFIED ==========
document.addEventListener('DOMContentLoaded', function () {
    const equipmentSelect = document.querySelector('select[name="equipment_instrumental"]');
    const referencePatternSelect = document.querySelector('select[name="reference_pattern"]');
    const parameterVerifiedSelect = document.querySelector('select[name="parameter_verified"]');

    if (!equipmentSelect || !referencePatternSelect) {
        console.warn('Campos equipment_instrumental o reference_pattern no encontrados');
        return;
    }

    /**
     * Carga los ReferencePattern y el parameter_verified asociados a un equipment_instrumental específico
     * @param {string} equipmentId - UUID del EquipmentInstrumental
     */
    function loadEquipmentData(equipmentId) {
        if (!equipmentId) {
            // Limpiar el select si no hay equipment seleccionado
            referencePatternSelect.innerHTML = '<option value="">---------</option>';
            referencePatternSelect.disabled = true;

            if (parameterVerifiedSelect) {
                parameterVerifiedSelect.value = '';
            }
            return;
        }

        // Mostrar estado de carga
        referencePatternSelect.disabled = true;
        referencePatternSelect.innerHTML = '<option value="">Cargando...</option>';

        // Realizar la solicitud AJAX
        axios.get(`/equipment/get_equipment_data/${equipmentId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(function (response) {
                const patterns = response.data.patterns || [];
                const unitTolerance = response.data.unit_tolerance || '';

                // ========== CARGAR REFERENCE PATTERNS ==========
                // Limpiar opciones anteriores
                referencePatternSelect.innerHTML = '<option value="">---------</option>';

                if (patterns.length === 0) {
                    referencePatternSelect.innerHTML = '<option value="">No hay patrones disponibles</option>';
                    referencePatternSelect.disabled = true;
                } else {
                    // Agregar nuevas opciones
                    patterns.forEach(pattern => {
                        const option = document.createElement('option');
                        option.value = pattern.id;
                        option.textContent = `${pattern.description_pattern} - ${pattern.magnitude_pattern} ${pattern.unit_pattern}`;
                        option.dataset.magnitude = pattern.magnitude_pattern;
                        referencePatternSelect.appendChild(option);
                    });
                    referencePatternSelect.disabled = false;
                }

                // ========== CARGAR PARAMETER_VERIFIED ==========
                if (parameterVerifiedSelect && unitTolerance) {
                    // Buscar la opción que coincida con el unit_tolerance
                    const options = parameterVerifiedSelect.querySelectorAll('option');
                    let found = false;

                    options.forEach(option => {
                        if (option.textContent.trim() === unitTolerance || option.value === unitTolerance) {
                            parameterVerifiedSelect.value = option.value;
                            found = true;
                        }
                    });

                    if (!found) {
                        console.warn(`No se encontró opción que coincida con: ${unitTolerance}`);
                        parameterVerifiedSelect.value = '';
                    }
                }
            })
            .catch(function (error) {
                console.error('Error al cargar los datos del equipo:', error);
                referencePatternSelect.innerHTML = '<option value="">Error al cargar patrones</option>';
                referencePatternSelect.disabled = true;

                let errorMsg = 'Error al cargar los datos del equipo';
                if (error.response && error.response.data && error.response.data.error) {
                    errorMsg = error.response.data.error;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: errorMsg,
                });
            });
    }

    /**
     * Event listener para cambios en equipment_instrumental
     */
    equipmentSelect.addEventListener('change', function () {
        const equipmentId = this.value;
        loadEquipmentData(equipmentId);
    });

    /**
     * Cargar datos al iniciar si ya hay un equipment seleccionado
     * (útil para edición de registros existentes)
     */
    if (equipmentSelect.value) {
        loadEquipmentData(equipmentSelect.value);
    } else {
        referencePatternSelect.disabled = true;
    }
});
// // ========== CARGA DINÁMICA DE REFERENCE PATTERN ==========
// document.addEventListener('DOMContentLoaded', function() {
//     const equipmentSelect = document.querySelector('select[name="equipment_instrumental"]');
//     const referencePatternSelect = document.querySelector('select[name="reference_pattern"]');
//
//     if (!equipmentSelect || !referencePatternSelect) {
//         console.warn('Campos equipment_instrumental o reference_pattern no encontrados');
//         return;
//     }
//
//     /**
//      * Carga los ReferencePattern asociados a un equipment_instrumental específico
//      * @param {string} equipmentId - UUID del EquipmentInstrumental
//      */
//     function loadReferencePatterns(equipmentId) {
//         if (!equipmentId) {
//             // Limpiar el select si no hay equipment seleccionado
//             referencePatternSelect.innerHTML = '<option value="">---------</option>';
//             referencePatternSelect.disabled = true;
//             return;
//         }
//
//         // Mostrar estado de carga
//         referencePatternSelect.disabled = true;
//         referencePatternSelect.innerHTML = '<option value="">Cargando...</option>';
//
//         // Realizar la solicitud AJAX
//         axios.get(`/equipment/get_reference_patterns/${equipmentId}/`, {
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest'
//             }
//         })
//         .then(function(response) {
//             const patterns = response.data.patterns || [];
//
//             // Limpiar opciones anteriores
//             referencePatternSelect.innerHTML = '<option value="">---------</option>';
//
//             if (patterns.length === 0) {
//                 referencePatternSelect.innerHTML = '<option value="">No hay patrones disponibles</option>';
//                 referencePatternSelect.disabled = true;
//                 return;
//             }
//
//             // Agregar nuevas opciones
//             patterns.forEach(pattern => {
//                 const option = document.createElement('option');
//                 option.value = pattern.id;
//                 option.textContent = `${pattern.description_pattern} - ${pattern.magnitude_pattern} ${pattern.unit_pattern}`;
//                 option.dataset.magnitude = pattern.magnitude_pattern;
//                 referencePatternSelect.appendChild(option);
//             });
//
//             referencePatternSelect.disabled = false;
//         })
//         .catch(function(error) {
//             console.error('Error al cargar los patrones:', error);
//             referencePatternSelect.innerHTML = '<option value="">Error al cargar patrones</option>';
//             referencePatternSelect.disabled = true;
//
//             let errorMsg = 'Error al cargar los patrones de referencia';
//             if (error.response && error.response.data && error.response.data.error) {
//                 errorMsg = error.response.data.error;
//             }
//
//             Swal.fire({
//                 icon: 'error',
//                 title: 'Error',
//                 text: errorMsg,
//             });
//         });
//     }
//
//     /**
//      * Event listener para cambios en equipment_instrumental
//      */
//     equipmentSelect.addEventListener('change', function() {
//         const equipmentId = this.value;
//         loadReferencePatterns(equipmentId);
//     });
//
//     /**
//      * Cargar patrones al iniciar si ya hay un equipment seleccionado
//      * (útil para edición de registros existentes)
//      */
//     if (equipmentSelect.value) {
//         loadReferencePatterns(equipmentSelect.value);
//     } else {
//         referencePatternSelect.disabled = true;
//     }
// });