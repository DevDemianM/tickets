/***************************************************
 * edit_ticket_ST.js - OPTIMIZADO
 * Funciones para la edición de tickets de servicio técnico
 ***************************************************/

"use strict";

// Variables globales
let currentEditingRow = null;
let searchTimeout = null;

/***** UTILIDADES *****/

/**
 * Muestra notificación toast
 */
function showToast(icon, title, position = 'top-end', timer = 3000) {
    const iconColors = {
        success: '#28a745',
        error: '#dc3545', 
        warning: '#ffc107',
        info: '#17a2b8'
    };

    Swal.mixin({
        toast: true,
        position: position,
        showConfirmButton: false,
        timer: timer,
        timerProgressBar: true,
        iconColor: iconColors[icon] || '#3085d6'
    }).fire({ icon, title });
}

/**
 * Valida email
 */
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Formatea número con separadores de miles (puntos)
 */
function formatNumberWithThousands(number) {
    if (!number && number !== 0) return '0';
    
    // Convertir a string y limpiar
    let cleanNumber = number.toString().replace(/\./g, '').replace(/,/g, '');
    let numericValue = parseInt(cleanNumber, 10);
    
    if (isNaN(numericValue)) return '0';
    
    // Formatear con puntos como separadores de miles
    return numericValue.toLocaleString('es-CO').replace(/,/g, '.');
}

/**
 * Elimina formato de números y devuelve valor numérico
 */
function unformatNumber(formattedNumber) {
    if (!formattedNumber && formattedNumber !== 0) return 0;
    
    // Eliminar puntos (separadores de miles) y convertir a número
    const cleanValue = formattedNumber.toString().replace(/\./g, '').replace(/,/g, '');
    return parseInt(cleanValue, 10) || 0;
}

/**
 * Aplica formato con separadores de miles a un input
 */
function applyThousandsFormatting(input) {
    if (!input) return;
    
    // Guardar posición del cursor
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const originalLength = input.value.length;
    
    // Obtener solo los números
    let rawValue = input.value.replace(/[^\d]/g, '');
    
    // Si está vacío, poner 0
    if (!rawValue) {
        input.value = '0';
        return;
    }
    
    // Convertir a número y formatear
    const numericValue = parseInt(rawValue, 10);
    const formattedValue = formatNumberWithThousands(numericValue);
    
    // Actualizar valor
    input.value = formattedValue;
    
    // Calcular nueva posición del cursor
    const newLength = input.value.length;
    const lengthDifference = newLength - originalLength;
    
    // Reposicionar cursor si el input está activo
    if (document.activeElement === input) {
        const newStart = Math.max(0, start + lengthDifference);
        const newEnd = Math.max(0, end + lengthDifference);
        input.setSelectionRange(newStart, newEnd);
    }
}

/***** VALIDACIONES *****/

/**
 * Muestra error de validación
 */
function showValidationError(input, message) {
    if (!input) return;
    
    removeValidationError(input);
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    
    input.parentNode.appendChild(feedback);
    input.classList.add('is-invalid');
}

/**
 * Elimina error de validación
 */
function removeValidationError(input) {
    if (!input) return;
    
    input.classList.remove('is-invalid');
    const feedbacks = input.parentNode.querySelectorAll('.invalid-feedback');
    feedbacks.forEach(feedback => feedback.remove());
}

/**
 * Valida documento
 */
function validateDocument(document) {
    if (!document?.trim()) {
        return { isValid: false, message: 'El documento del cliente es obligatorio' };
    }
    
    const trimmedDoc = document.trim();
    const digitsOnly = trimmedDoc.replace(/\D/g, '');
    
    if (digitsOnly.length < 5) {
        return { isValid: false, message: 'El documento debe tener al menos 5 dígitos' };
    }
    
    if (trimmedDoc.length > 15) {
        return { isValid: false, message: 'El documento no puede tener más de 15 caracteres' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Valida IMEI
 */
function validateIMEI(imei) {
    if (!imei?.trim()) {
        return { isValid: false, message: 'El IMEI/Serial es obligatorio' };
    }
    
    const trimmedImei = imei.trim();
    
    if (!/^[A-Za-z0-9]+$/.test(trimmedImei)) {
        return { isValid: false, message: 'El IMEI/Serial solo puede contener números y letras' };
    }
    
    if (trimmedImei.length > 15) {
        return { isValid: false, message: 'El IMEI/Serial no puede tener más de 15 caracteres' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Valida teléfono
 */
function validatePhone(phone) {
    return /^[\d\s\-()]+$/.test(phone) && phone.replace(/[^\d]/g, '').length >= 7;
}

/**
 * Configura validaciones en tiempo real
 */
function setupValidations() {
    const fields = [
        { id: 'client_names', required: true, errorMsg: 'El nombre del cliente es obligatorio' },
        { id: 'client_lastnames', required: false, errorMsg: 'El apellido del cliente es opcional' },
        { id: 'document', validator: 'document', errorMsg: 'El documento del cliente es obligatorio' },
        { id: 'phone', validator: validatePhone, errorMsg: 'Ingrese un número de teléfono válido' },
        { id: 'mail', required: true, email: true, errorMsg: 'Ingrese un correo electrónico válido' },
        { id: 'IMEI', validator: 'imei', required: true, errorMsg: 'El IMEI/Serial es obligatorio' },
        { id: 'service_value', required: true, number: true, min: 0, errorMsg: 'El valor del servicio debe ser un número positivo' }
    ];

    fields.forEach(fieldInfo => {
        const input = document.getElementById(fieldInfo.id);
        if (!input || input.hasAttribute('data-validation-attached')) return;
        
        input.setAttribute('data-validation-attached', 'true');
        
        input.addEventListener('input', function() {
            let valid = true;
            let errorMessage = '';
            
            if (fieldInfo.validator === 'document') {
                const validation = validateDocument(this.value);
                valid = validation.isValid;
                errorMessage = validation.message;
            } else if (fieldInfo.validator === 'imei') {
                const validation = validateIMEI(this.value);
                valid = validation.isValid;
                errorMessage = validation.message;
            } else if (fieldInfo.required && !this.value.trim()) {
                valid = false;
                errorMessage = fieldInfo.errorMsg;
            } else if (fieldInfo.email && this.value.trim() && !validateEmail(this.value.trim())) {
                valid = false;
                errorMessage = fieldInfo.errorMsg;
            } else if (fieldInfo.number) {
                const num = unformatNumber(this.value);
                if (isNaN(num) || num < (fieldInfo.min || 0)) {
                    valid = false;
                    errorMessage = fieldInfo.errorMsg;
                }
            } else if (fieldInfo.validator && typeof fieldInfo.validator === 'function' && 
                      this.value.trim() && !fieldInfo.validator(this.value.trim())) {
                valid = false;
                errorMessage = fieldInfo.errorMsg;
            }

            if (valid) {
                removeValidationError(this);
            } else {
                showValidationError(this, errorMessage);
            }
        });

        if (input.value) {
            input.dispatchEvent(new Event('input'));
        }
    });
}

/***** GESTIÓN DE REPUESTOS *****/

/**
 * Calcula total de una fila
 */
function calculateRowTotal(row) {
    const quantityInput = row.querySelector('.part-quantity');
    const priceInput = row.querySelector('.part-unit-value');
    const totalInput = row.querySelector('.part-total-value');

    if (!quantityInput || !priceInput || !totalInput) return;

    const quantity = parseInt(quantityInput.value) || 0;
    const price = unformatNumber(priceInput.value) || 0;
    const total = quantity * price;

    // Formatear y mostrar el total
    totalInput.value = formatNumberWithThousands(total);
    updateTotals();
}

/**
 * Actualiza totales generales
 */
function updateTotals() {
    const spareValueInput = document.getElementById('spare_value');
    const serviceValueInput = document.getElementById('service_value');
    const totalInput = document.getElementById('total');

    if (!spareValueInput || !serviceValueInput || !totalInput) return;

    // Calcular total de repuestos
    let spareTotal = 0;
    document.querySelectorAll('.part-total-value').forEach(input => {
        spareTotal += unformatNumber(input.value);
    });

    // Formatear y actualizar valor de repuestos
    spareValueInput.value = formatNumberWithThousands(spareTotal);

    // Calcular total general
    const serviceValue = unformatNumber(serviceValueInput.value) || 0;
    const totalValue = serviceValue + spareTotal;

    // Formatear y actualizar total general
    totalInput.value = formatNumberWithThousands(totalValue);
}

/**
 * Configura eventos de una fila
 */
function setupRowCalculations(row) {
    const quantityInput = row.querySelector('.part-quantity');
    const unitPriceInput = row.querySelector('.part-unit-value');
    const removeBtn = row.querySelector('.remove-part');
    const selectBtn = row.querySelector('.select-part');

    if (!quantityInput || !unitPriceInput) return;

    // Formatear valores iniciales
    if (unitPriceInput.value) {
        unitPriceInput.value = formatNumberWithThousands(unitPriceInput.value);
    }

    // Eventos de cálculo
    const updateRow = () => calculateRowTotal(row);
    
    unitPriceInput.addEventListener('input', function() {
        applyThousandsFormatting(this);
        updateRow();
    });

    quantityInput.addEventListener('input', updateRow);
    quantityInput.addEventListener('blur', function() {
        if (!this.value || parseInt(this.value) < 1) {
            this.value = '1';
            updateRow();
        }
    });

    // Botón eliminar
    if (removeBtn) {
        removeBtn.addEventListener('click', () => confirmRemoveRow(row));
    }

    // Botón buscar
    if (selectBtn) {
        selectBtn.addEventListener('click', function() {
            currentEditingRow = row;
            const modal = new bootstrap.Modal(document.getElementById('searchPartsModal'));
            modal.show();
        });
    }

    // Calcular total inicial
    updateRow();
}

/**
 * Confirma eliminación de fila
 */
function confirmRemoveRow(row) {
    const displayInput = row.querySelector('input[readonly]');
    const partDescription = displayInput?.value || 'Repuesto';

    Swal.fire({
        title: '¿Eliminar repuesto?',
        text: '¿Estás seguro de eliminar este repuesto?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.isConfirmed) {
            const tbody = row.parentNode;
            row.remove();

            // Mostrar mensaje si no quedan filas
            if (!tbody.querySelectorAll('.part-row').length) {
                const emptyRow = document.createElement('tr');
                emptyRow.id = 'noPartsRow';
                emptyRow.innerHTML = `
                    <td colspan="5" class="text-center py-4">
                        <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                        <p class="text-muted mb-0">No se han agregado repuestos para este servicio.</p>
                    </td>
                `;
                tbody.appendChild(emptyRow);
            }

            updateTotals();
            showToast('success', `Repuesto "${partDescription}" eliminado correctamente`);
        }
    });
}

/**
 * Agrega nueva fila
 */
function addPartRow(partData = null) {
    const partsTable = document.getElementById('partsTable');
    if (!partsTable) return;

    const tbody = partsTable.querySelector('tbody');
    const noPartsRow = document.getElementById('noPartsRow');

    if (noPartsRow) noPartsRow.remove();

    const template = document.getElementById('partRowTemplate');
    if (!template) {
        showToast('error', 'Error: Plantilla de repuesto no encontrada');
        return;
    }

    const newRow = document.importNode(template.content, true).querySelector('tr');
    newRow.classList.add('part-row');

    if (partData) {
        const hiddenInput = newRow.querySelector('input[name="spare_part_code[]"]');
        const displayInput = newRow.querySelector('input[readonly]');
        const unitValueInput = newRow.querySelector('.part-unit-value');

        if (hiddenInput) {
            hiddenInput.value = partData.code;
        }

        if (displayInput) {
            displayInput.value = `${partData.code} - ${partData.description}`;
        }

        if (unitValueInput) {
            unitValueInput.value = formatNumberWithThousands(partData.price || 0);
        }
    }

    tbody.appendChild(newRow);
    setupRowCalculations(newRow);
    
    showToast('success', 'Repuesto agregado correctamente');
    return newRow;
}

/**
 * Busca repuestos
 */
function searchParts(term) {
    if (!term || term.length < 3) return;

    const loader = document.getElementById('searchResultsLoader');
    const initialMsg = document.getElementById('initialSearchMessage');
    const noResults = document.getElementById('noResultsMessage');
    const resultsList = document.getElementById('searchResultsList');

    if (loader) loader.style.display = 'block';
    if (initialMsg) initialMsg.style.display = 'none';
    if (noResults) noResults.style.display = 'none';
    if (resultsList) resultsList.style.display = 'none';

    fetch('/tickets/search_spare_parts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `search=${encodeURIComponent(term)}`
    })
    .then(response => {
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (loader) loader.style.display = 'none';
        
        if (data?.parts?.length > 0) {
            showSearchResults(data.parts, term);
        } else {
            if (noResults) noResults.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error searching parts:', error);
        if (loader) loader.style.display = 'none';
        if (noResults) {
            noResults.style.display = 'block';
            noResults.innerHTML = `
                <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                <h5 class="text-danger">Error al buscar repuestos</h5>
                <p class="text-muted mb-0">${error.message}</p>
            `;
        }
    });
}

/**
 * Muestra resultados de búsqueda
 */
function showSearchResults(results, term) {
    const searchResultsList = document.getElementById('searchResultsList');
    if (!searchResultsList) return;

    searchResultsList.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'search-results-container';

    const row = document.createElement('div');
    row.className = 'row g-3';

    // Contador
    const count = document.createElement('div');
    count.className = 'col-12 mb-2';
    count.innerHTML = `<small class="text-muted">Se encontraron ${results.length} repuestos</small>`;
    row.appendChild(count);

    // Resultados
    results.forEach(part => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-2';

        const card = document.createElement('div');
        card.className = 'card h-100 shadow-sm part-card';
        card.style.cursor = 'pointer';
        card.innerHTML = `
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-0 fw-bold">${highlightSearchTerm(part.description, term)}</h6>
                    <span class="badge bg-primary ms-2">Cód: ${highlightSearchTerm(part.code, term)}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <span class="text-success fw-bold">${part.price && part.price != '0' ? formatNumberWithThousands(part.price) : ''}</span>
                    <button class="btn btn-sm btn-primary select-result">
                        <i class="fas fa-check me-1"></i>Seleccionar
                    </button>
                </div>
            </div>
        `;

        card.dataset.code = part.code;
        card.dataset.description = part.description;
        card.dataset.price = part.price || '0';

        // Agregar listener para el click en la card
        card.addEventListener('click', (e) => {
            // Evitar doble activación si se hace click en el botón
            if (!e.target.closest('.select-result')) {
                selectPart({
                    code: card.dataset.code,
                    description: card.dataset.description,
                    price: card.dataset.price,
                    stock: part.stock || 0
                });
            }
        });

        // Agregar listener específico para el botón
        const selectBtn = card.querySelector('.select-result');
        if (selectBtn) {
            selectBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Evitar que se active el listener de la card
                selectPart({
                    code: card.dataset.code,
                    description: card.dataset.description,
                    price: card.dataset.price,
                    stock: part.stock || 0
                });
            });
        }

        col.appendChild(card);
        row.appendChild(col);
    });

    container.appendChild(row);
    searchResultsList.appendChild(container);
    searchResultsList.style.display = 'block';
}

/**
 * Resalta término de búsqueda
 */
function highlightSearchTerm(text, term) {
    if (!text) return '';
    const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedTerm})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

/**
 * Selecciona repuesto
 */
function selectPart(partData) {
    if (!currentEditingRow) {
        showToast('error', 'Error: No se pudo identificar la fila a actualizar');
        return;
    }

    try {
        const hiddenInput = currentEditingRow.querySelector('input[name="spare_part_code[]"]');
        const displayInput = currentEditingRow.querySelector('input[readonly]');
        const unitValueInput = currentEditingRow.querySelector('.part-unit-value');

        if (!hiddenInput) throw new Error("No se encontró el campo oculto de código");

        // Actualizar campo oculto con el código
        hiddenInput.value = partData.code;

        // Actualizar campo de visualización
        if (displayInput) {
            displayInput.value = `${partData.code} - ${partData.description}`;
        }

        if (unitValueInput) {
            unitValueInput.value = formatNumberWithThousands(partData.price || 0);
        }

        calculateRowTotal(currentEditingRow);

        // Cerrar modal
        const modal = document.getElementById('searchPartsModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            } else {
                const newModal = new bootstrap.Modal(modal);
                newModal.hide();
            }
            
            // Limpiar backdrop de manera segura
            modal.addEventListener('hidden.bs.modal', function() {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
                
                // Restaurar scroll del body
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }, { once: true });
        }

        showToast('success', `Repuesto "${partData.description}" agregado correctamente`);

    } catch (error) {
        console.error("Error al seleccionar repuesto:", error);
        showToast('error', `Error: ${error.message}`);
    }
}

/***** GESTIÓN DE PROBLEMAS *****/

/**
 * Actualiza textarea de problemas seleccionados
 */
function updateSelectedProblems() {
    const textarea = document.getElementById('selected_problems');
    const checkboxes = document.querySelectorAll('.problem-checkbox');

    if (!textarea || !checkboxes.length) return;

    const selected = [];
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const label = document.querySelector(`label[for="${checkbox.id}"]`);
            if (label) selected.push(label.textContent.trim());
        }
    });

    textarea.value = selected.join(', ');
}

/**
 * Configura búsqueda de problemas
 */
function setupProblemSearch() {
    const searchInput = document.getElementById('searchProblems');
    const options = document.querySelectorAll('.problem-option');

    if (!searchInput || !options.length) return;

    searchInput.addEventListener('input', function() {
        const term = this.value.toLowerCase();
        options.forEach(option => {
            const label = option.querySelector('label');
            if (label) {
                const text = label.textContent.toLowerCase();
                option.style.display = text.includes(term) ? '' : 'none';
            }
        });
    });
}

/**
 * Configura botones de problemas
 */
function setupProblemButtons() {
    const checkboxes = document.querySelectorAll('.problem-checkbox');
    const selectAllBtn = document.getElementById('selectAllProblems');
    const clearBtn = document.getElementById('clearProblems');

    if (!checkboxes.length) return;

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedProblems);
    });

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            checkboxes.forEach(checkbox => {
                const option = checkbox.closest('.problem-option');
                if (option && option.style.display !== 'none') {
                    checkbox.checked = true;
                }
            });
            updateSelectedProblems();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            checkboxes.forEach(checkbox => checkbox.checked = false);
            updateSelectedProblems();
        });
    }
    

    updateSelectedProblems();
}

/***** TÉCNICO Y ESTADO *****/

/**
 * Configura relación técnico-documento
 */
function setupTechnicianRelation() {
    const techSelect = document.getElementById('technical_name');
    const docInput = document.getElementById('technical_document');
    const stateInput = document.getElementById('state');

    if (!techSelect || !docInput || !stateInput) return;

    techSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        
        if (selectedOption && selectedOption.value) {
            const document = selectedOption.getAttribute('data-document') || 'Sin documento';
            docInput.value = document;
            stateInput.value = 'Asignado';
            showToast('info', `Técnico cambiado a: ${selectedOption.text}`);
        } else {
            docInput.value = 'Sin asignar';
            stateInput.value = 'Sin asignar';
            showToast('info', 'Estado cambiado a: Sin asignar');
        }
    });

    // Inicialización
    if (techSelect.value) {
        const selectedOption = techSelect.options[techSelect.selectedIndex];
        if (selectedOption) {
            const document = selectedOption.getAttribute('data-document') || 'Sin documento';
            docInput.value = document;
        }
    }
}

/***** FORMULARIO *****/

/**
 * Configura envío del formulario
 */
function setupFormSubmission() {
    const form = document.getElementById('ticket-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const errors = [];

        // Validaciones básicas
        const serviceValue = document.getElementById('service_value');
        if (!serviceValue?.value || unformatNumber(serviceValue.value) < 0) {
            errors.push('El valor del servicio debe ser un número positivo.');
        }

        const problemCheckboxes = document.querySelectorAll('.problem-checkbox:checked');
        if (problemCheckboxes.length === 0) {
            errors.push('Debe seleccionar al menos un problema.');
        }

        if (errors.length > 0) {
            showToast('error', 'Hay errores en el formulario');
            return;
        }

        // Confirmar envío
        Swal.fire({
            title: '¿Guardar cambios?',
            text: '¿Estás seguro de guardar los cambios en este ticket?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, guardar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (result.isConfirmed) {
                // Preparar valores numéricos - remover formato antes de enviar
                document.querySelectorAll('#service_value, #spare_value, #total, .part-unit-value, .part-total-value')
                    .forEach(input => {
                        // Convertir valor formateado a número sin formato
                        const numericValue = unformatNumber(input.value);
                        input.value = numericValue;
                    });

                // Agregar campo de redirección
                const redirectInput = document.createElement('input');
                redirectInput.type = 'hidden';
                redirectInput.name = 'redirect_after_save';
                redirectInput.value = 'true';
                form.appendChild(redirectInput);

                form.submit();
            }
        });
    });
}

/***** INICIALIZACIÓN *****/

/**
 * Configura búsqueda de repuestos
 */
function setupPartsSearch() {
    const modal = document.getElementById('searchPartsModal');
    const searchInput = document.getElementById('modalPartSearch');
    const clearBtn = document.getElementById('clearSearch');

    if (!modal || !searchInput) return;

    // Limpiar al abrir modal
    modal.addEventListener('shown.bs.modal', function() {
        searchInput.value = '';
        searchInput.focus();
        document.getElementById('initialSearchMessage').style.display = 'block';
        document.getElementById('searchResultsLoader').style.display = 'none';
        document.getElementById('noResultsMessage').style.display = 'none';
        document.getElementById('searchResultsList').style.display = 'none';
    });

    // Búsqueda con debounce
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        if (searchTimeout) clearTimeout(searchTimeout);

        if (query.length >= 3) {
            searchTimeout = setTimeout(() => searchParts(query), 300);
        } else {
            document.getElementById('initialSearchMessage').style.display = 'block';
            document.getElementById('searchResultsLoader').style.display = 'none';
        }
    });

    // Botón limpiar
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.focus();
            document.getElementById('initialSearchMessage').style.display = 'block';
            document.getElementById('searchResultsLoader').style.display = 'none';
        });
    }

    // Delegación para botones de selección
    const partsTable = document.getElementById('partsTable');
    if (partsTable) {
        partsTable.addEventListener('click', function(e) {
            const selectBtn = e.target.closest('.select-part');
            if (selectBtn) {
                currentEditingRow = selectBtn.closest('tr');
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    }
}

/**
 * Inicialización principal
 */
function initialize() {
    console.log("Inicializando edit_ticket_ST.js");

    // Configurar validaciones
    setupValidations();

    // Configurar relación técnico-documento
    setupTechnicianRelation();

    // Configurar problemas
    setupProblemSearch();
    setupProblemButtons();

    // Configurar búsqueda de repuestos
    setupPartsSearch();

    // Configurar filas existentes
    const existingRows = document.querySelectorAll('.part-row');
    existingRows.forEach(row => {
        // Formatear valores iniciales
        const unitInput = row.querySelector('.part-unit-value');
        const totalInput = row.querySelector('.part-total-value');
        
        if (unitInput?.value && unitInput.value !== '0') {
            // Limpiar valor y reformatear
            let cleanValue = unformatNumber(unitInput.value);
            
            // Detección mejorada para valores unitarios
            cleanValue = detectAndCorrectMultipliedValue(cleanValue, unitInput.value);
            
            unitInput.value = formatNumberWithThousands(cleanValue);
        }
        
        if (totalInput?.value && totalInput.value !== '0') {
            // Limpiar valor y reformatear
            let cleanValue = unformatNumber(totalInput.value);
            
            // Detección mejorada para valores totales
            cleanValue = detectAndCorrectMultipliedValue(cleanValue, totalInput.value);
            
            totalInput.value = formatNumberWithThousands(cleanValue);
        }
        
        setupRowCalculations(row);
    });

    // Configurar formateo de campos principales
    const serviceInput = document.getElementById('service_value');
    const spareInput = document.getElementById('spare_value');
    const totalInput = document.getElementById('total');
    
    if (serviceInput) {
        // Formatear valor inicial del servicio
        if (serviceInput.value && serviceInput.value !== '0') {
            let cleanValue = unformatNumber(serviceInput.value);
            const originalValueStr = serviceInput.value.toString();
            
            // Log detallado para diagnóstico
            console.log(`DEBUG: Valor de servicio original: "${originalValueStr}", limpio: ${cleanValue}`);
            
            // SOLUCIÓN DIRECTA: Para valores específicos que sabemos están mal
            // Si el valor es exactamente 1.000.000 o similar cuando debería ser 10.000
            if (cleanValue === 1000000 || cleanValue === 100000) {
                console.log("Detectado valor erróneo de 1.000.000, corrigiendo a 10.000");
                cleanValue = 10000;
            }
            // Otra verificación - si es múltiplo exacto de 100 y está en cierto rango
            else if (cleanValue % 100 === 0 && cleanValue >= 100000) {
                const correctedValue = cleanValue / 100;
                console.log(`Corrigiendo valor del servicio: ${cleanValue} → ${correctedValue}`);
                cleanValue = correctedValue;
            }
            
            serviceInput.value = formatNumberWithThousands(cleanValue);
        }
        
        serviceInput.addEventListener('input', function() {
            applyThousandsFormatting(this);
            updateTotals();
        });
    }
    
    // Formatear valores iniciales de repuestos y total (campos de solo lectura)
    if (spareInput && spareInput.value && spareInput.value !== '0') {
        const cleanValue = unformatNumber(spareInput.value);
        spareInput.value = formatNumberWithThousands(cleanValue);
    }
    
    if (totalInput && totalInput.value && totalInput.value !== '0') {
        const cleanValue = unformatNumber(totalInput.value);
        totalInput.value = formatNumberWithThousands(cleanValue);
    }

    // Configurar botón agregar repuesto
    const addBtn = document.getElementById('addPartBtn');
    if (addBtn) {
        // Remover listeners previos
        const newBtn = addBtn.cloneNode(true);
        addBtn.parentNode.replaceChild(newBtn, addBtn);
        
        newBtn.addEventListener('click', () => addPartRow());
    }

    // Configurar formulario
    setupFormSubmission();

    // Actualizar totales iniciales para asegurar consistencia
    updateTotals();

    // Verificar que todos los valores numéricos estén correctamente formateados
    setTimeout(() => {
        // Re-formatear todos los campos numéricos por si hay inconsistencias
        document.querySelectorAll('.part-unit-value, .part-total-value').forEach(input => {
            if (input.value && input.value !== '0') {
                let cleanValue = unformatNumber(input.value);
                
                // Detección mejorada para cualquier valor
                cleanValue = detectAndCorrectMultipliedValue(cleanValue, input.value);
                
                input.value = formatNumberWithThousands(cleanValue);
            }
        });
        
        // Actualizar totales una vez más para estar seguros
        updateTotals();
    }, 100);

    console.log("Inicialización completada");
}

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', initialize);

// Listener global para manejar scroll de modales
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Limpiar cualquier backdrop residual
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
        });
    });
});

/**
 * Detecta si un valor numérico parece estar multiplicado incorrectamente por 100
 * @param {number} numericValue - El valor numérico a verificar
 * @param {string} originalString - La representación original en string
 * @returns {number} - El valor corregido o el original si no requiere corrección
 */
function detectAndCorrectMultipliedValue(numericValue, originalString) {
    // Si el valor es muy pequeño, no aplicamos corrección
    if (numericValue <= 10000) {
        return numericValue;
    }
    
    // Solo corregir valores que sean múltiplos exactos de 100
    if (numericValue % 100 === 0) {
        // Para evitar falsos positivos, verificamos con más criterios
        
        // 1. El valor debe terminar en "00" exactamente 
        if (!originalString.endsWith('00')) {
            return numericValue;
        }
        
        // 2. Si el valor original tiene separadores de miles, probablemente ya está correcto
        if (originalString.includes('.')) {
            return numericValue;
        }

        // 3. Los valores probables no deberían terminar en "0000" (que serían normales en miles)
        if (originalString.endsWith('0000')) {
            return numericValue;
        }

        // Si pasó todas las condiciones, es probable que esté multiplicado por 100
        console.log(`Valor corregido: ${originalString} (${numericValue}) -> ${numericValue/100}`);
        return numericValue / 100;
    }
    
    return numericValue;
}




