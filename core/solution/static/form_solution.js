// document.addEventListener('DOMContentLoaded', function () {
//     const soluteReagentField = document.querySelector('select[name="solute_std"]');
//     const concentrationField = document.querySelector('input[name="concentration_std"]');
//     const concentrationUnitField = document.querySelector('select[name="concentration_unit"]');
//     const quantitySolutionField = document.querySelector('input[name="quantity_solution_std"]');
//     const solventReagentField = document.querySelector('select[name="solvent_reagent"]');
//
//     // Campos que se deben bloquear cuando ready_to_use es True
//     const fieldsToToggle = [
//         'concentration_std',
//         'concentration_unit',
//         'quantity_solution_std',
//         'solvent_reagent'
//     ];
//
//     // Función para obtener datos del reactivo seleccionado via AJAX
//     async function fetchReagentData(reagentId) {
//         if (!reagentId) return null;
//
//         try {
//             const response = await fetch(`/solution/api/inventory-reagent/${reagentId}/`);
//             if (!response.ok) throw new Error('Error al obtener datos');
//             const data = await response.json();
//             return data;
//         } catch (error) {
//             console.error('Error al obtener datos del reactivo:', error);
//             return null;
//         }
//     }
//
//     // Función para mostrar el mensaje de "Estándar listo para usar"
//     function showReadyToUseMessage() {
//         let messageDiv = document.getElementById('ready-to-use-message');
//
//         if (!messageDiv) {
//             messageDiv = document.createElement('div');
//             messageDiv.id = 'ready-to-use-message';
//             messageDiv.className = 'alert alert-info alert-dismissible fade show';
//             messageDiv.style.marginTop = '15px';
//             messageDiv.style.marginBottom = '15px';
//             messageDiv.innerHTML = `
//                 <div class="d-flex align-items-center">
//                     <i class="fas fa-info-circle fa-2x me-3"></i>
//                     <div>
//                         <h6 class="alert-heading mb-1">
//                             <strong>Estándar Listo para Usar</strong>
//                         </h6>
//                         <p class="mb-0">
//                             Los campos concentración y cantidad se han completado automáticamente.
//                         </p>
//                     </div>
//                 </div>
//                 <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
//             `;
//
//             // Insertar el mensaje después del campo solute_std
//             if (solventReagentField && solventReagentField.parentElement) {
//                 solventReagentField.parentElement.after(messageDiv);
//             } else {
//                 // Alternativa: insertar al inicio del formulario
//                 const form = document.querySelector('form');
//                 if (form) {
//                     form.insertBefore(messageDiv, form.firstChild);
//                 }
//             }
//         }
//
//         // Mostrar el mensaje
//         messageDiv.style.display = 'block';
//     }
//
//     // Función para ocultar el mensaje
//     function hideReadyToUseMessage() {
//         const messageDiv = document.getElementById('ready-to-use-message');
//         if (messageDiv) {
//             messageDiv.style.display = 'none';
//         }
//     }
//
//     async function checkAndToggleFields() {
//         let shouldBeReadonly = false;
//         let reagentData = null;
//
//         // Verificar si el reactivo seleccionado tiene ready_to_use = True
//         if (soluteReagentField && soluteReagentField.value) {
//             reagentData = await fetchReagentData(soluteReagentField.value);
//
//             if (reagentData && reagentData.reagent && reagentData.reagent.ready_to_use === true) {
//                 shouldBeReadonly = true;
//                 showReadyToUseMessage();
//             } else {
//                 hideReadyToUseMessage();
//             }
//         } else {
//             hideReadyToUseMessage();
//         }
//
//         // Aplicar readonly/disabled a los campos
//         fieldsToToggle.forEach(fieldName => {
//             const field = document.querySelector(`[name="${fieldName}"]`);
//             if (field) {
//                 if (shouldBeReadonly) {
//                     // Hacer readonly o disabled según el tipo de campo
//                     if (field.tagName === 'SELECT') {
//                         field.setAttribute('disabled', 'disabled');
//                         // Crear campo hidden para enviar el valor al servidor
//                         let hiddenField = document.querySelector(`input[name="${fieldName}_hidden"]`);
//                         if (!hiddenField) {
//                             hiddenField = document.createElement('input');
//                             hiddenField.type = 'hidden';
//                             hiddenField.name = fieldName;
//                             field.parentNode.appendChild(hiddenField);
//                         }
//                         hiddenField.value = field.value;
//                     } else {
//                         field.setAttribute('readonly', 'readonly');
//                     }
//                     field.style.backgroundColor = '#e9ecef';
//                     field.style.cursor = 'not-allowed';
//                 } else {
//                     // Quitar readonly/disabled
//                     if (field.tagName === 'SELECT') {
//                         field.removeAttribute('disabled');
//                         // Eliminar campo hidden si existe
//                         const hiddenField = document.querySelector(`input[name="${fieldName}_hidden"]`);
//                         if (hiddenField) {
//                             hiddenField.remove();
//                         }
//                     } else {
//                         field.removeAttribute('readonly');
//                     }
//                     field.style.backgroundColor = '';
//                     field.style.cursor = '';
//                 }
//             }
//         });
//
//         // Si debe estar en readonly (ready_to_use = True), cargar datos automáticamente
//         if (shouldBeReadonly && reagentData) {
//             loadReadyToUseData(reagentData);
//         }
//     }
//
//     function loadReadyToUseData(data) {
//         if (!data) return;
//
//         // Asignar valores de pureza a concentración
//         if (data.purity && concentrationField) {
//             concentrationField.value = data.purity;
//         }
//
//         // Asignar unidad de pureza a unidad de concentración
//         if (data.reagent && data.reagent.purity_unit && concentrationUnitField) {
//             concentrationUnitField.value = data.reagent.purity_unit;
//         }
//
//         // Asignar cantidad en stock a cantidad de solución
//         if (data.quantity_stock && quantitySolutionField) {
//             quantitySolutionField.value = data.quantity_stock;
//         }
//
//         // Limpiar/vaciar el campo de solvente ya que no se necesita
//         if (solventReagentField) {
//             solventReagentField.value = '';
//         }
//     }
//
//     // Event listener para cuando cambie el reactivo soluto
//     if (soluteReagentField) {
//         // Ejecutar al cargar si ya hay un valor seleccionado
//         if (soluteReagentField.value) {
//             checkAndToggleFields();
//         }
//
//         soluteReagentField.addEventListener('change', function () {
//             checkAndToggleFields();
//         });
//     }
//
//     // Prevenir el envío de campos disabled (asegurar que los hidden fields funcionen)
//     const form = document.querySelector('form');
//     if (form) {
//         form.addEventListener('submit', function (e) {
//             // Re-habilitar temporalmente campos disabled para que se envíen
//             // o asegurar que los hidden fields tengan los valores correctos
//             fieldsToToggle.forEach(fieldName => {
//                 const field = document.querySelector(`[name="${fieldName}"]`);
//                 const hiddenField = document.querySelector(`input[name="${fieldName}_hidden"]`);
//
//                 if (field && field.hasAttribute('disabled') && hiddenField) {
//                     hiddenField.value = field.value;
//                 }
//             });
//         });
//     }
// });


document.addEventListener('DOMContentLoaded', function() {
    const soluteReagentField = document.querySelector('select[name="solute_std"]');
    const concentrationField = document.querySelector('input[name="concentration_std"]');
    const concentrationUnitField = document.querySelector('select[name="concentration_unit"]');
    const quantitySolutionField = document.querySelector('input[name="quantity_solution_std"]');
    const solventReagentField = document.querySelector('select[name="solvent_reagent"]');

    // Campos que se deben bloquear cuando ready_to_use es True
    const fieldsToToggle = [
        'concentration_std',
        'concentration_unit',
        'quantity_solution_std',
        'solvent_reagent'
    ];

    // Función para obtener datos del reactivo seleccionado via AJAX
    async function fetchReagentData(reagentId) {
        if (!reagentId) return null;

        try {
            const response = await fetch(`/solution/api/inventory-reagent/${reagentId}/`);
            if (!response.ok) throw new Error('Error al obtener datos');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error al obtener datos del reactivo:', error);
            return null;
        }
    }

    // Función para mostrar el mensaje de "Estándar listo para usar"
    function showReadyToUseMessage() {
        let messageDiv = document.getElementById('ready-to-use-message');

        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.id = 'ready-to-use-message';
            messageDiv.className = 'alert alert-info alert-dismissible fade show';
            messageDiv.style.marginTop = '15px';
            messageDiv.style.marginBottom = '15px';
            messageDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-info-circle fa-2x me-3"></i>
                    <div>
                        <h6 class="alert-heading mb-1">
                            <strong>Estándar Listo para Usar</strong>
                        </h6>
                        <p class="mb-0">
                            Los campos de concentración y cantidad se han completado automáticamente.
                        </p>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            // Insertar el mensaje después del campo solute_std
            if (solventReagentField && solventReagentField.parentElement) {
                solventReagentField.parentElement.after(messageDiv);
            } else {
                // Alternativa: insertar al inicio del formulario
                const form = document.querySelector('form');
                if (form) {
                    form.insertBefore(messageDiv, form.firstChild);
                }
            }
        }

        // Mostrar el mensaje
        messageDiv.style.display = 'block';
    }

    // Función para ocultar el mensaje
    function hideReadyToUseMessage() {
        const messageDiv = document.getElementById('ready-to-use-message');
        if (messageDiv) {
            messageDiv.style.display = 'none';
        }
    }

    // Función para crear campo hidden
    function createHiddenField(field, fieldName) {
        // Buscar si ya existe un campo hidden
        let hiddenField = document.getElementById(`hidden_${fieldName}`);

        if (!hiddenField) {
            hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.id = `hidden_${fieldName}`;
            hiddenField.name = fieldName; // IMPORTANTE: usar el mismo nombre
            hiddenField.className = 'hidden-field-backup';
            field.parentNode.appendChild(hiddenField);
        }

        hiddenField.value = field.value;
        return hiddenField;
    }

    // Función para remover campo hidden
    function removeHiddenField(fieldName) {
        const hiddenField = document.getElementById(`hidden_${fieldName}`);
        if (hiddenField) {
            hiddenField.remove();
        }
    }

    async function checkAndToggleFields() {
        let shouldBeReadonly = false;
        let reagentData = null;

        // Verificar si el reactivo seleccionado tiene ready_to_use = True
        if (soluteReagentField && soluteReagentField.value) {
            reagentData = await fetchReagentData(soluteReagentField.value);

            if (reagentData && reagentData.reagent && reagentData.reagent.ready_to_use === true) {
                shouldBeReadonly = true;
                showReadyToUseMessage();
            } else {
                hideReadyToUseMessage();
            }
        } else {
            hideReadyToUseMessage();
        }

        // Aplicar readonly/disabled a los campos
        fieldsToToggle.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                if (shouldBeReadonly) {
                    // Hacer readonly o disabled según el tipo de campo
                    if (field.tagName === 'SELECT') {
                        field.setAttribute('disabled', 'disabled');
                        // Crear campo hidden para enviar el valor al servidor
                        createHiddenField(field, fieldName);
                    } else {
                        field.setAttribute('readonly', 'readonly');
                    }
                    field.style.backgroundColor = '#e9ecef';
                    field.style.cursor = 'not-allowed';
                } else {
                    // Quitar readonly/disabled
                    if (field.tagName === 'SELECT') {
                        field.removeAttribute('disabled');
                        // Eliminar campo hidden si existe
                        removeHiddenField(fieldName);
                    } else {
                        field.removeAttribute('readonly');
                    }
                    field.style.backgroundColor = '';
                    field.style.cursor = '';
                }
            }
        });

        // Si debe estar en readonly (ready_to_use = True), cargar datos automáticamente
        if (shouldBeReadonly && reagentData) {
            loadReadyToUseData(reagentData);
        }
    }

    function loadReadyToUseData(data) {
        if (!data) return;

        // Asignar valores de pureza a concentración
        if (data.purity && concentrationField) {
            concentrationField.value = data.purity;
        }

        // Asignar unidad de pureza a unidad de concentración
        if (data.reagent && data.reagent.purity_unit && concentrationUnitField) {
            concentrationUnitField.value = data.reagent.purity_unit;
            // Actualizar el hidden field con el nuevo valor
            createHiddenField(concentrationUnitField, 'concentration_unit');
        }

        // Asignar cantidad en stock a cantidad de solución
        if (data.quantity_stock && quantitySolutionField) {
            quantitySolutionField.value = data.quantity_stock;
        }

        // Limpiar/vaciar el campo de solvente ya que no se necesita
        if (solventReagentField) {
            solventReagentField.value = '';
            // Actualizar el hidden field
            createHiddenField(solventReagentField, 'solvent_reagent');
        }
    }

    // Event listener para cuando cambie el reactivo soluto
    if (soluteReagentField) {
        // Ejecutar al cargar si ya hay un valor seleccionado
        if (soluteReagentField.value) {
            checkAndToggleFields();
        }

        soluteReagentField.addEventListener('change', function() {
            checkAndToggleFields();
        });
    }

    // CRÍTICO: Antes de enviar el formulario, asegurar que los valores se envíen correctamente
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Asegurar que los hidden fields tengan los valores correctos
            fieldsToToggle.forEach(fieldName => {
                const field = document.querySelector(`[name="${fieldName}"]`);

                if (field && field.hasAttribute('disabled')) {
                    // Actualizar el hidden field con el valor actual
                    createHiddenField(field, fieldName);
                }
            });
        });
    }
});
