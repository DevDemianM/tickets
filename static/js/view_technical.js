/**
 * view_technical.js - Vista del técnico
 * 
 * NOTA IMPORTANTE SOBRE COMPATIBILIDAD:
 * -------------------------------------
 * Este archivo maneja la vista del técnico con selectores de estado simplificados:
 * 
 * 1. Solo permite ciertos estados: Asignado, En proceso, En Revision
 * 2. Las peticiones AJAX usan el parámetro 'status' (diferente de otros módulos)
 * 3. El backend en view_technical acepta 'status' en lugar de 'state'
 * 4. Mantiene validaciones de retroceso y confirmaciones
 * 
 * Esta diferencia es intencional para el flujo del técnico.
 */

/***************************************************
 * view_technical.js
 * Funciones para la vista del técnico
 ***************************************************/

/***** Funciones de Notificación *****/

/**
 * Muestra un toast (notificación pequeña) usando SweetAlert2.
 * @param {string} icon - Tipo de ícono ('success', 'error', 'info', etc.).
 * @param {string} title - Texto a mostrar.
 * @param {string} [position='top-end'] - Posición del toast.
 * @param {number} [timer=3000] - Tiempo en milisegundos.
 */
function showToast(icon, title, position = 'top-end', timer = 3000) {
    const Toast = Swal.mixin({
        toast: true,
        position: position,
        showConfirmButton: false,
        timer: timer,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });
    Toast.fire({ icon: icon, title: title });
}

/**
 * Muestra una alerta de éxito (usada tras actualizar un ticket).
 * @param {Function} [callback] - Función opcional a ejecutar después de cerrar la alerta
 */
function showSuccessTicketAlert(callback) {
    Swal.fire({
        icon: 'success',
        title: '¡Operación exitosa!',
        text: 'El ticket ha sido actualizado correctamente.',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        iconColor: '#28a745',
        customClass: {
            popup: 'colored-toast'
        },
        didClose: () => {
            if (typeof callback === 'function') {
                callback();
            }
        }
    });
}

/***** Funcionalidad Principal *****/
// Esperar a que jQuery esté disponible
(function() {
    function initializeWhenReady() {
        if (typeof $ === 'undefined' || typeof jQuery === 'undefined') {
            setTimeout(initializeWhenReady, 50);
            return;
        }
        
        $(document).ready(function() {
    // Verificar si venimos de una actualización exitosa
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('ticket_updated') === 'success') {
        showSuccessTicketAlert();
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('ticket_created') === 'success') {
        showSuccessTicketAlert();
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // --- Búsqueda en la tabla de tickets (IDÉNTICA A TECHNICAL_SERVICE) ---
    const searchInput = $("#searchInput");
    const ticketsTable = $("#ticketsTable");
    if (searchInput.length && ticketsTable.length) {
        searchInput.on("input", function () {
            const searchValue = this.value.toLowerCase();
            const rows = ticketsTable.find("tr");
            for (let i = 1; i < rows.length; i++) {
                let rowText = rows[i].textContent.toLowerCase();
                rows[i].style.display = rowText.includes(searchValue) ? "" : "none";
            }
            setTimeout(updatePaginationAfterFilter, 100);
        });
    }

    // --- Configuración de cambio de estados AJAX (IDÉNTICA A TECHNICAL_SERVICE) ---
    setupStatusSelects();

    // --- Filtros por Botones Server-Side (IDÉNTICA A TECHNICAL_SERVICE) ---
    setupClientSideFilters();
        });
    }
    
    initializeWhenReady();
})();

/***** Funciones de Búsqueda y Filtros *****/

/**
 * Configuración de filtros SERVER-SIDE por botones (IDÉNTICA A TECHNICAL_SERVICE)
 */
function setupClientSideFilters() {
    // Variables para mantener estado de filtros
    let currentStateFilter = 'Todos';
    let currentCityFilter = 'Todas las ciudades';
    let currentSearch = '';

    // Función para aplicar filtros SERVER-SIDE
    window.applyCurrentFilters = function() {
            const selectedStatus = $('input[name="filterStatus"]:checked').next('label').text().trim();
            const selectedCity = $('input[name="filterCity"]:checked').next('label').text().trim();
        const searchText = $('#searchInput').val().toLowerCase().trim();
        
        currentStateFilter = selectedStatus;
        currentCityFilter = selectedCity;
        currentSearch = searchText;
        
        // Actualizar URL y hacer petición al servidor
        updateFilterURLAndReload();
    };
    
    // Función para actualizar URL y recargar con filtros server-side
    function updateFilterURLAndReload() {
        const params = new URLSearchParams();
        
        // Siempre empezar en página 1 cuando se cambian filtros
        params.set('page', '1');
        
        if (currentStateFilter && currentStateFilter !== 'Todos') {
            params.set('state', currentStateFilter);
        }
        
        if (currentCityFilter && currentCityFilter !== 'Todas las ciudades') {
            params.set('city', currentCityFilter);
        }
        
        if (currentSearch) {
            params.set('search', currentSearch);
        }
        
        // Recargar la página con los nuevos parámetros
        const newUrl = window.location.pathname + '?' + params.toString();
        window.location.href = newUrl;
    }
    
    // Event handlers para filtros
        $('input[name="filterStatus"]').on('change', function () {
        $('input[name="filterStatus"]').next('label').removeClass('active');
        $(this).next('label').addClass('active');
        
        // Mostrar indicador de carga
        showToast('info', 'Aplicando filtro...', 'top-end', 1500);
        
        // Aplicar filtros con pequeño delay para mostrar el toast
        setTimeout(() => {
            window.applyCurrentFilters();
        }, 100);
    });

    $('input[name="filterCity"]').on('change', function () {
        $('input[name="filterCity"]').next('label').removeClass('active');
        $(this).next('label').addClass('active');
        
        // Mostrar indicador de carga
        showToast('info', 'Aplicando filtro...', 'top-end', 1500);
        
        // Aplicar filtros con pequeño delay para mostrar el toast
        setTimeout(() => {
            window.applyCurrentFilters();
        }, 100);
    });

    $('#searchInput').on('input', debounce(function() {
        // Mostrar indicador de carga para búsqueda
        if ($(this).val().trim()) {
            showToast('info', 'Buscando...', 'top-end', 1000);
        }
        
        setTimeout(() => {
            window.applyCurrentFilters();
        }, 100);
    }, 800)); // Más tiempo de debounce para búsqueda
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Inicializar filtros desde URL (solo visual, no recargar)
    initializeFiltersFromURL();
    
    function initializeFiltersFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const stateFromURL = urlParams.get('state') || 'Todos';
        const cityFromURL = urlParams.get('city') || 'Todas las ciudades';
        const searchFromURL = urlParams.get('search') || '';
        
        // Solo configurar visualmente los botones activos
        $('input[name="filterStatus"]').each(function() {
            const labelText = $(this).next('label').text().trim();
            if (labelText === stateFromURL) {
                $(this).prop('checked', true);
                $(this).next('label').addClass('active');
            }
        });
        
        $('input[name="filterCity"]').each(function() {
            const labelText = $(this).next('label').text().trim();
            if (labelText === cityFromURL) {
                $(this).prop('checked', true);
                $(this).next('label').addClass('active');
            }
        });
        
        $('#searchInput').val(searchFromURL);
        
        // Actualizar variables internas
        currentStateFilter = stateFromURL;
        currentCityFilter = cityFromURL;
        currentSearch = searchFromURL;
        
        // NO aplicar filtros aquí - los datos ya vienen filtrados del servidor
    }
}

/**
 * Función debounce para limitar llamadas frecuentes
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Función global para limpiar todos los filtros
 */
window.clearAllFilters = function() {
    $('input[name="filterStatus"][id="btnTodos"]').prop('checked', true);
    $('input[name="filterCity"][id="btnAllCities"]').prop('checked', true);
    $('#searchInput').val('');
    
    $('input[name="filterStatus"], input[name="filterCity"]').next('label').removeClass('active');
    $('input[name="filterStatus"]:checked, input[name="filterCity"]:checked').next('label').addClass('active');
    
    window.applyCurrentFilters();
};

/**
 * FUNCIÓN OBSOLETA - Mantenida para compatibilidad
 * Ahora se usa applyCurrentFilters()
 */
function updateURL(params) {
    console.warn('updateURL() está obsoleta. Usar applyCurrentFilters() en su lugar.');
    
    const url = new URL(window.location);
    
    // Actualizar parámetros
    Object.keys(params).forEach(key => {
        if (params[key] && params[key] !== '' && params[key] !== 'Todos' && params[key] !== 'Todas') {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    
    // Recargar página con nuevos parámetros
    window.location.href = url.toString();
}

// 🆕 SISTEMA DE CAMBIO DE ESTADOS - VIEW TECHNICAL
// Adaptado desde Reparación Interna para la vista del técnico

/**
 * Configuración de los selects de estado para cambios AJAX (IDÉNTICA A TECHNICAL_SERVICE)
 */
function setupStatusSelects() {
        const stateOrder = {
            "Sin asignar": 1,
            "Asignado": 2,
            "En proceso": 3,
            "En Revision": 4,
            "Terminado": 5
        };

        const stateTimestampMap = {
            "Asignado": "assigned",
            "En proceso": "in_progress",
            "En Revision": "in_revision",
            "Terminado": "finished",
            "Recibido": "received"
        };

        $('.status-select').each(function() {
            const $select = $(this);
            if (!$select.attr('data-original-state')) {
                $select.attr('data-original-state', $select.val());
            }
            
            const currentState = $select.val();
            $select.closest('tr').attr('data-status', currentState);
            
            if (currentState in stateTimestampMap) {
                const timestampClass = stateTimestampMap[currentState];
                $select.closest('tr').find(`.${timestampClass}-timestamp`).addClass('active-timestamp');
            }
        });

        $('.status-select').on('change', function () {
            const $select = $(this);
            const ticketId = $select.data('ticket-id');
            const newStatus = $select.val();
            const originalValue = $select.attr('data-original-state');
            
            if (stateOrder[newStatus] < stateOrder[originalValue]) {
                Swal.fire({
                    icon: 'error',
                    title: 'Operación no permitida',
                    text: `No se puede cambiar el estado de "${originalValue}" a "${newStatus}". No se permite retroceder en el flujo de estados.`,
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'Entendido'
                });
                
                $select.val(originalValue);
                return false;
            }

            let confirmText = `¿Estás seguro de cambiar el estado del ticket #${ticketId} a "${newStatus}"?`;
            
            if (newStatus === "Terminado") {
                confirmText += `\n\nIMPORTANTE: Una vez que el ticket esté en estado "Terminado", ya no podrá ser editado.`;
            }

            Swal.fire({
                title: '¿Cambiar estado?',
                text: confirmText,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, cambiar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                updateTicketStatusAjax($select, ticketId, newStatus, originalValue);
            } else {
                $select.val(originalValue);
            }
        });
    });
}

/**
 * Actualiza el estado del ticket via AJAX (IDÉNTICA A TECHNICAL_SERVICE)
 */
function updateTicketStatusAjax($select, ticketId, newStatus, originalValue) {
                    $select.addClass('opacity-50');
                    $select.prop('disabled', true);

                    showToast('info', 'Actualizando estado...', 'top-end');

                    $.ajax({
                        url: '/tickets/update_ticket_status_ajax',
                        method: 'POST',
                        data: {
                            ticket_id: ticketId,
            state: newStatus
                        },
                        success: function (response) {
                            $select.removeClass('opacity-50');
                            $select.prop('disabled', false);

                            if (response.success) {
                                $select.attr('data-original-state', newStatus);
                                
                                const $row = $select.closest('tr');
                                $row.attr('data-status', newStatus);
                                
                                if (newStatus === "Terminado") {
                                    const editButton = $row.find('button.btn-outline-secondary');
                                    editButton.addClass('disabled');
                                    editButton.attr('title', 'No se puede editar un ticket en estado Terminado');
                                    editButton.attr('disabled', true);
                                }

                // Reaplica filtros activos después del cambio
                if (typeof window.applyCurrentFilters === 'function') {
                    window.applyCurrentFilters();
                }

                showToast('success', 'Estado actualizado correctamente');
                                            } else {
                showToast('error', response.message || 'Error al actualizar el estado');
                                $select.val(originalValue);
                            }
                        },
                        error: function (xhr) {
                            $select.removeClass('opacity-50');
                            $select.prop('disabled', false);
                            $select.val(originalValue);
                            
                            let errorMsg = 'Error al actualizar el estado';
                            if (xhr.responseJSON && xhr.responseJSON.message) {
                                errorMsg = xhr.responseJSON.message;
                            }
            showToast('error', errorMsg);
        }
    });
}

/***** Funciones para Detalle de Ticket *****/

let selectedFiles = [];

function validateFiles(fileInput, maxFiles = 5, maxSize = 5) {
    const files = fileInput.files;
    if (files.length > maxFiles) {
        showToast('error', `Máximo ${maxFiles} archivos permitidos`);
        fileInput.value = '';
        return false;
    }
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.match('image.*')) {
            showToast('error', `El archivo "${file.name}" no es una imagen válida`);
            fileInput.value = '';
            return false;
        }
        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > maxSize) {
            showToast('error', `El archivo "${file.name}" excede el tamaño máximo de ${maxSize}MB`);
            fileInput.value = '';
            return false;
        }
    }
    return true;
}

function initImageUpload() {
    $('#images').on('change', function() {
        if (validateFiles(this)) {
            selectedFiles = Array.from(this.files);
            updatePreview();
        }
    });
}

function updatePreview() {
    const previewContainer = $('#image-preview');
    previewContainer.empty();
    
    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageHtml = `
                <div class="col-md-3 mb-2 image-preview-item" data-index="${index}">
                    <div class="card">
                        <img src="${e.target.result}" class="card-img-top" style="height: 150px; object-fit: cover;">
                        <div class="card-body p-2">
                            <button type="button" class="btn btn-sm btn-danger remove-image" data-index="${index}">
                                <i class="fas fa-trash"></i> Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            previewContainer.append(imageHtml);
        };
        reader.readAsDataURL(file);
    });
    
    previewContainer.off('click').on('click', '.remove-image', function() {
        const index = $(this).data('index');
        selectedFiles.splice(index, 1);
        updatePreview();
    });
}

$(document).ready(function() {
    if ($('#images').length) {
        initImageUpload();
    }
});

/**
 * Función para actualizar el contador de tickets visibles (IDÉNTICA A TECHNICAL_SERVICE)
 */
function updateTicketCounter() {
    const visibleTickets = $('#ticketsTable tbody tr:visible').not('#noResultsRow, #noResultsRowFiltered').length;
    $('.badge.bg-primary strong').text(visibleTickets);
}

/**
 * Muestra mensaje de "no hay resultados" (IDÉNTICA A TECHNICAL_SERVICE)
 */
function showNoResultsMessage(show) {
    if (show) {
        if ($('#noResultsRowFiltered').length === 0) {
            const colspan = $('#ticketsTable thead th').length;
            const noResultsRow = `
                <tr id="noResultsRowFiltered">
                    <td colspan="${colspan}" class="text-center py-5">
                        <i class="fas fa-filter fa-3x mb-3 text-muted"></i>
                        <p class="text-muted">No hay tickets que coincidan con los filtros seleccionados.</p>
                        <button class="btn btn-outline-secondary btn-sm" onclick="clearAllFilters()">
                            <i class="fas fa-times me-1"></i>Limpiar filtros
                        </button>
                    </td>
                </tr>
            `;
            $('#ticketsTable tbody').append(noResultsRow);
        }
        $('#noResultsRowFiltered').show();
    } else {
        $('#noResultsRowFiltered').remove();
    }
}

/**
 * Función global para limpiar todos los filtros (IDÉNTICA A TECHNICAL_SERVICE)
 */
window.clearAllFilters = function() {
    $('input[name="filterStatus"][id="btnTodos"]').prop('checked', true);
    $('input[name="filterCity"][id="btnAllCities"]').prop('checked', true);
    $('#searchInput').val('');
    
    $('input[name="filterStatus"], input[name="filterCity"]').next('label').removeClass('active');
    $('input[name="filterStatus"]:checked, input[name="filterCity"]:checked').next('label').addClass('active');
    
    window.applyCurrentFilters();
};

/**
 * Actualiza la paginación después de filtrar o modificar la tabla (IDÉNTICA A TECHNICAL_SERVICE)
 */
window.updatePaginationAfterFilter = function() {
    updateTicketCounter();
};