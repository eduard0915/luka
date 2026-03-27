// ========== INICIALIZACIÓN DE DATE Y DATETIME PICKERS ==========

// Función para inicializar DatePickers (solo fecha)
function initDatePickers() {
    const dateInputs = document.querySelectorAll('[data-datepicker="1"]:not([data-datetime="1"])');

    dateInputs.forEach(function (input) {
        if (input.dataset.datepickerInitialized) return;

        input.classList.add('form-control');

        if (!input.dataset.datepickerEnhanced) {
            const group = document.createElement('div');
            group.className = 'input-group';
            const parent = input.parentNode;
            parent.insertBefore(group, input);
            group.appendChild(input);

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-outline-secondary';
            btn.setAttribute('aria-label', 'Abrir calendario');
            btn.innerHTML = '<i class="bi bi-calendar-date"></i>';
            group.appendChild(btn);
            input.dataset.datepickerEnhanced = '1';

            const dp = new Datepicker(input, {
                autohide: true,
                language: 'es',
                format: 'yyyy-mm-dd',
                todayHighlight: true,
                clearBtn: true,
                container: input.closest('.modal') || document.body,
                prevArrow: '<i class="bi bi-chevron-left"></i>',
                nextArrow: '<i class="bi bi-chevron-right"></i>',
                buttonClass: 'btn btn-outline-secondary'
            });

            btn.addEventListener('click', function () {
                dp.show();
            });
        }
        input.dataset.datepickerInitialized = '1';
    });
}

// Función para inicializar DateTimePickers (fecha + hora)
function initDateTimePickers() {
    const datetimeInputs = document.querySelectorAll('[data-datepicker="1"][data-datetime="1"]');

    datetimeInputs.forEach(function (input) {
        if (input.dataset.datetimeInitialized) return;

        input.classList.add('form-control');

        if (!input.dataset.datetimeEnhanced) {
            const group = document.createElement('div');
            group.className = 'input-group';
            const parent = input.parentNode;
            parent.insertBefore(group, input);
            group.appendChild(input);

            const btnDate = document.createElement('button');
            btnDate.type = 'button';
            btnDate.className = 'btn btn-outline-secondary';
            btnDate.setAttribute('aria-label', 'Abrir calendario');
            btnDate.innerHTML = '<i class="bi bi-calendar-date"></i>';
            group.appendChild(btnDate);

            const btnTime = document.createElement('button');
            btnTime.type = 'button';
            btnTime.className = 'btn btn-outline-secondary';
            btnTime.setAttribute('aria-label', 'Establecer hora');
            btnTime.innerHTML = '<i class="bi bi-clock"></i>';
            group.appendChild(btnTime);

            input.dataset.datetimeEnhanced = '1';

            const dp = new Datepicker(input, {
                autohide: true,
                language: 'es',
                format: 'yyyy-mm-dd',
                todayHighlight: true,
                clearBtn: false,
                container: input.closest('.modal') || document.body,
                prevArrow: '<i class="bi bi-chevron-left"></i>',
                nextArrow: '<i class="bi bi-chevron-right"></i>',
                buttonClass: 'btn btn-outline-secondary'
            });

            btnDate.addEventListener('click', function () {
                dp.show();
            });

            btnTime.addEventListener('click', function () {
                const currentValue = input.value;
                let currentDate = '';
                let currentTime = '';

                if (currentValue) {
                    const parts = currentValue.split(' ');
                    currentDate = parts[0] || '';
                    currentTime = parts[1] || '';
                } else {
                    const now = new Date();
                    currentDate = now.toISOString().split('T')[0];
                    currentTime = now.toTimeString().slice(0, 5);
                }

                const timeparts = currentTime.split(':');
                const currentHours = timeparts[0] || '00';
                const currentMinutes = timeparts[1] || '00';

                // Generar opciones de horas (00-23)
                let hoursOptions = '';
                for (let i = 0; i <= 23; i++) {
                    const hour = String(i).padStart(2, '0');
                    const selected = hour === currentHours ? 'selected' : '';
                    hoursOptions += `<option value="${hour}" ${selected}>${hour}</option>`;
                }

                // Generar opciones de minutos (00-59)
                let minutesOptions = '';
                for (let i = 0; i <= 59; i++) {
                    const minute = String(i).padStart(2, '0');
                    const selected = minute === currentMinutes ? 'selected' : '';
                    minutesOptions += `<option value="${minute}" ${selected}>${minute}</option>`;
                }

                const modalHtml = `
                    <div class="modal fade" id="timePickerModal" tabindex="-1">
                        <div class="modal-dialog modal-sm modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Seleccionar Hora</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label class="form-label">Hora (Formato 24h)</label>
                                        <div class="row g-2">
                                            <div class="col-6">
                                                <label class="form-label small">Horas</label>
                                                <select class="form-select" id="hoursSelect">
                                                    ${hoursOptions}
                                                </select>
                                            </div>
                                            <div class="col-6">
                                                <label class="form-label small">Minutos</label>
                                                <select class="form-select" id="minutesSelect">
                                                    ${minutesOptions}
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="d-grid gap-2">
                                        <button type="button" class="btn btn-sm btn-outline-primary" id="setNowBtn">
                                            <i class="bi bi-clock-fill me-1"></i>Hora Actual
                                        </button>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                    <button type="button" class="btn btn-primary" id="confirmTimeBtn">Aceptar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                const existingModal = document.getElementById('timePickerModal');
                if (existingModal) existingModal.remove();

                document.body.insertAdjacentHTML('beforeend', modalHtml);
                const modal = new bootstrap.Modal(document.getElementById('timePickerModal'));
                modal.show();

                const hoursSelect = document.getElementById('hoursSelect');
                const minutesSelect = document.getElementById('minutesSelect');

                // Scroll automático a la opción seleccionada
                setTimeout(() => {
                    const selectedHour = hoursSelect.querySelector('option[selected]');
                    const selectedMinute = minutesSelect.querySelector('option[selected]');
                    if (selectedHour) selectedHour.scrollIntoView({block: 'center'});
                    if (selectedMinute) selectedMinute.scrollIntoView({block: 'center'});
                }, 100);

                document.getElementById('setNowBtn').addEventListener('click', function () {
                    const now = new Date();
                    const nowHour = String(now.getHours()).padStart(2, '0');
                    const nowMinute = String(now.getMinutes()).padStart(2, '0');

                    hoursSelect.value = nowHour;
                    minutesSelect.value = nowMinute;

                    // Scroll a las opciones actuales
                    setTimeout(() => {
                        hoursSelect.querySelector(`option[value="${nowHour}"]`).scrollIntoView({block: 'center'});
                        minutesSelect.querySelector(`option[value="${nowMinute}"]`).scrollIntoView({block: 'center'});
                    }, 50);
                });

                document.getElementById('confirmTimeBtn').addEventListener('click', function () {
                    const hours = hoursSelect.value;
                    const minutes = minutesSelect.value;
                    const timeValue = `${hours}:${minutes}`;

                    input.value = `${currentDate} ${timeValue}`;
                    input.dispatchEvent(new Event('change', {bubbles: true}));
                    modal.hide();
                });

                document.getElementById('timePickerModal').addEventListener('hidden.bs.modal', function () {
                    this.remove();
                });
            });

            input.addEventListener('changeDate', function (e) {
                const selectedDate = e.detail.date;
                if (selectedDate) {
                    const dateStr = selectedDate.toISOString().split('T')[0];
                    const currentValue = input.value;
                    let timeStr = '00:00';

                    if (currentValue && currentValue.includes(' ')) {
                        timeStr = currentValue.split(' ')[1] || '00:00';
                    }

                    input.value = `${dateStr} ${timeStr}`;
                }
            });

            input.addEventListener('blur', function () {
                const value = this.value.trim();
                if (value) {
                    const regex = /^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$/;
                    if (!regex.test(value)) {
                        alert('Formato incorrecto. Use: yyyy-mm-dd HH:MM\nEjemplo: 2025-01-15 14:30');
                        this.focus();
                    }
                }
            });
        }
        input.dataset.datetimeInitialized = '1';
    });
}

// Inicializar pickers
initDatePickers();
initDateTimePickers();
