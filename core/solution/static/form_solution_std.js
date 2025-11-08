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
                            <strong>Estándar listo para usar</strong>
                        </h6>
                        <p class="mb-0">
                            Los campos de concentración y cantidad se han completado automáticamente.
                        </p>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            if (soluteReagentField && soluteReagentField.parentElement) {
                soluteReagentField.parentElement.after(messageDiv);
            } else {
                const form = document.querySelector('form');
                if (form) {
                    form.insertBefore(messageDiv, form.firstChild);
                }
            }
        }

        messageDiv.style.display = 'block';
    }

    // Función para ocultar el mensaje de ready to use
    function hideReadyToUseMessage() {
        const messageDiv = document.getElementById('ready-to-use-message');
        if (messageDiv) {
            messageDiv.style.display = 'none';
        }
    }

    async function checkAndToggleFields() {
        let shouldBeReadonly = false;
        let isVolumetric = false;
        let reagentData = null;

        // Verificar si el reactivo seleccionado tiene ready_to_use = True o volumetric = True
        if (soluteReagentField && soluteReagentField.value) {
            reagentData = await fetchReagentData(soluteReagentField.value);

            if (reagentData && reagentData.reagent) {
                // Verificar si es ready_to_use
                if (reagentData.reagent.ready_to_use === true) {
                    shouldBeReadonly = true;
                    showReadyToUseMessage();
                }
                // Verificar si es volumétrico
                else if (reagentData.reagent.volumetric === true) {
                    isVolumetric = true;
                    hideReadyToUseMessage();
                }
                else {
                    hideReadyToUseMessage();
                }
            }
        } else {
            hideReadyToUseMessage();
        }

        // Aplicar readonly/disabled a los campos según corresponda
        fieldsToToggle.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                // Para ready_to_use: bloquear todos los campos en fieldsToToggle
                if (shouldBeReadonly) {
                    if (field.tagName === 'SELECT') {
                        field.style.pointerEvents = 'none';
                        field.style.backgroundColor = '#e9ecef';
                        field.style.cursor = 'not-allowed';
                        field.setAttribute('data-readonly', 'true');
                    } else {
                        field.setAttribute('readonly', 'readonly');
                        field.style.backgroundColor = '#e9ecef';
                        field.style.cursor = 'not-allowed';
                    }
                }
                // Para volumétrico: solo bloquear concentration_unit
                else if (isVolumetric && fieldName === 'concentration_unit') {
                    if (field.tagName === 'SELECT') {
                        field.style.pointerEvents = 'none';
                        field.style.backgroundColor = '#e9ecef';
                        field.style.cursor = 'not-allowed';
                        field.setAttribute('data-readonly', 'true');
                    } else {
                        field.setAttribute('readonly', 'readonly');
                        field.style.backgroundColor = '#e9ecef';
                        field.style.cursor = 'not-allowed';
                    }
                }
                // Caso normal: desbloquear
                else {
                    if (field.tagName === 'SELECT') {
                        field.style.pointerEvents = '';
                        field.style.backgroundColor = '';
                        field.style.cursor = '';
                        field.removeAttribute('data-readonly');
                    } else {
                        field.removeAttribute('readonly');
                        field.style.backgroundColor = '';
                        field.style.cursor = '';
                    }
                }
            }
        });

        // Cargar datos según el tipo de reactivo
        if (shouldBeReadonly && reagentData) {
            loadReadyToUseData(reagentData);
        } else if (isVolumetric && reagentData) {
            loadVolumetricData(reagentData);
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
        }

        // Asignar cantidad en stock a cantidad de solución
        if (data.quantity_stock && quantitySolutionField) {
            quantitySolutionField.value = data.quantity_stock;
        }

        // Limpiar/vaciar el campo de solvente ya que no se necesita
        if (solventReagentField) {
            solventReagentField.value = '';
        }
    }

    function loadVolumetricData(data) {
        if (!data || !data.reagent) return;

        // Para volumétrico: solo establecer la unidad de concentración
        if (data.reagent.purity_unit && concentrationUnitField) {
            concentrationUnitField.value = data.reagent.purity_unit;
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

    // CRÍTICO: Antes de enviar el formulario
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Los valores se enviarán correctamente porque no usamos disabled
            // Solo usamos pointer-events y readonly visual
        });
    }
});