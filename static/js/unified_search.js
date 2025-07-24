/**
 * Sistema de búsqueda unificado para todos los módulos de tickets
 * Implementación limpia que respeta el diseño existente
 */
const UnifiedSearch = {
    modules: {
        'technical_service': {
            searchUrl: '/tickets/search_tickets',
            tableBodyId: 'ticketsTableBody',
            searchInputId: 'searchInput'
        },
        'internal_repair': {
            searchUrl: '/tickets/search_tickets', 
            tableBodyId: 'repairsTableBody',
            searchInputId: 'searchRepairs'
        },
        'warranty': {
            searchUrl: '/tickets/search_tickets',
            tableBodyId: 'ticketsTableBody',
            searchInputId: 'searchInput'
        },
        'view_technical': {
            searchUrl: '/tickets/search_tickets',
            tableBodyId: 'ticketsTableBody',
            searchInputId: 'searchInput'
        }
    },
    
    currentModule: null,
    isSearchActive: false,
    originalContent: null,
    
    init: function(moduleName) {
        this.currentModule = moduleName;
        const config = this.modules[moduleName];
        
        if (!config) {
            console.error(`Módulo de búsqueda no configurado: ${moduleName}`);
            return;
        }
        
        this.setupSearchInterface(config);
        this.bindEvents(config);
        
        console.log(`✅ Sistema de búsqueda unificado inicializado para: ${moduleName}`);
    },
    
    setupSearchInterface: function(config) {
        const searchInput = document.getElementById(config.searchInputId);
        
        if (!searchInput) {
            return;
        }
        
        // Encontrar el ícono de búsqueda existente
        const inputGroup = searchInput.closest('.input-group');
        const searchIcon = inputGroup?.querySelector('.input-group-text .fas.fa-search');
        
        if (searchIcon && inputGroup) {
            // Convertir el ícono en un botón clickeable manteniendo el mismo estilo
            const iconContainer = searchIcon.closest('.input-group-text');
            iconContainer.style.cursor = 'pointer';
            iconContainer.className = 'input-group-text bg-primary text-white';
            iconContainer.title = 'Buscar tickets';
            
            // Agregar ID para el evento
            iconContainer.id = 'searchButton';
            
            // Crear botón de limpiar (se mostrará cuando haya búsqueda activa)
            this.createClearButton(inputGroup);
            
            // Crear área de mensajes
            this.createMessageArea(config);
        }
    },
    
    createClearButton: function(inputGroup) {
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'btn btn-outline-secondary btn-sm ms-2';
        clearButton.id = 'clearSearchButton';
        clearButton.innerHTML = '<i class="fas fa-times me-1"></i>Limpiar';
        clearButton.style.display = 'none';
        
        // Insertar después del input-group
        inputGroup.parentNode.insertBefore(clearButton, inputGroup.nextSibling);
    },
    
    createMessageArea: function(config) {
        const messageDiv = document.createElement('div');
        messageDiv.id = 'searchResultMessage';
        messageDiv.className = 'alert alert-info mt-2 mx-2';
        messageDiv.style.display = 'none';
        
        // Insertar antes de la tabla
        const tableCard = document.getElementById(config.tableBodyId)?.closest('.card');
        if (tableCard) {
            tableCard.parentNode.insertBefore(messageDiv, tableCard);
        }
    },
    
    bindEvents: function(config) {
        const searchInput = document.getElementById(config.searchInputId);
        const searchButton = document.getElementById('searchButton');
        const clearButton = document.getElementById('clearSearchButton');
        
        // Evento del botón de búsqueda (ícono)
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                this.performSearch(config);
            });
        }
        
        // Evento del input (Enter)
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(config);
                }
            });
            
            // Mostrar/ocultar botón de limpiar
            searchInput.addEventListener('input', () => {
                if (clearButton) {
                    const hasText = searchInput.value.trim().length > 0;
                    clearButton.style.display = hasText ? 'inline-block' : 'none';
                }
            });
        }
        
        // Evento del botón de limpiar
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearSearch(config);
            });
        }
    },
    
    performSearch: function(config) {
        const searchInput = document.getElementById(config.searchInputId);
        const searchTerm = searchInput?.value?.trim();
        
        if (!searchTerm) {
            this.showToast('warning', 'Por favor ingresa un término de búsqueda');
            return;
        }
        
        // Guardar contenido original si es la primera búsqueda
        if (!this.isSearchActive) {
            this.saveOriginalContent(config);
        }
        
        // Mostrar indicador de carga
        this.showLoading(config);
        
        // Realizar petición AJAX
        const formData = new FormData();
        formData.append('search', searchTerm);
        
        fetch(config.searchUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            this.handleSearchResponse(data, config);
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
            this.showToast('error', 'Error al realizar la búsqueda');
            this.hideLoading(config);
        });
    },
    
    handleSearchResponse: function(data, config) {
        this.hideLoading(config);
        
        if (data.status === 'success') {
            // Actualizar tabla con resultados
            const tableBody = document.getElementById(config.tableBodyId);
            if (tableBody && data.html) {
                tableBody.innerHTML = data.html;
            }
            
            // Mostrar mensaje de resultados
            this.showSearchMessage(config, data.message, data.total_results);
            
            // Ocultar paginación durante búsqueda
            this.hidePagination();
            
            // Marcar búsqueda como activa
            this.isSearchActive = true;
            
        } else {
            this.showToast('error', data.message || 'Error en la búsqueda');
        }
    },
    
    clearSearch: function(config) {
        const searchInput = document.getElementById(config.searchInputId);
        const clearButton = document.getElementById('clearSearchButton');
        const searchButton = document.getElementById('searchButton');
        
        // Limpiar input
        if (searchInput) {
            searchInput.value = '';
        }
        
        // Ocultar botón de limpiar
        if (clearButton) {
            clearButton.style.display = 'none';
        }
        
        // Restaurar ícono original
        if (searchButton) {
            searchButton.className = 'input-group-text bg-light';
            searchButton.title = '';
        }
        
        // Restaurar contenido original
        if (this.isSearchActive && this.originalContent) {
            this.restoreOriginalContent(config);
        }
        
        // Ocultar mensaje de búsqueda
        this.hideSearchMessage(config);
        
        // Restaurar paginación
        this.showPagination();
        
        // Resetear estado
        this.isSearchActive = false;
        this.originalContent = null;
    },
    
    saveOriginalContent: function(config) {
        const tableBody = document.getElementById(config.tableBodyId);
        if (tableBody) {
            this.originalContent = tableBody.innerHTML;
        }
    },
    
    restoreOriginalContent: function(config) {
        const tableBody = document.getElementById(config.tableBodyId);
        if (tableBody && this.originalContent) {
            tableBody.innerHTML = this.originalContent;
        }
    },
    
    showLoading: function(config) {
        const tableBody = document.getElementById(config.tableBodyId);
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Buscando...</span>
                        </div>
                        <div class="mt-2">Buscando tickets...</div>
                    </td>
                </tr>
            `;
        }
    },
    
    hideLoading: function(config) {
        // El loading se oculta cuando se actualiza con resultados
    },
    
    showSearchMessage: function(config, message, totalResults) {
        const messageContainer = document.getElementById('searchResultMessage');
        if (messageContainer) {
            messageContainer.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span><i class="fas fa-search me-2"></i>${message}</span>
                    <span class="badge bg-primary">${totalResults} resultado(s)</span>
                </div>
            `;
            messageContainer.style.display = 'block';
        }
    },
    
    hideSearchMessage: function(config) {
        const messageContainer = document.getElementById('searchResultMessage');
        if (messageContainer) {
            messageContainer.style.display = 'none';
        }
    },
    
    hidePagination: function() {
        const paginationElements = document.querySelectorAll('.card-footer, nav[aria-label*="Paginación"]');
        paginationElements.forEach(element => {
            element.style.display = 'none';
        });
    },
    
    showPagination: function() {
        const paginationElements = document.querySelectorAll('.card-footer, nav[aria-label*="Paginación"]');
        paginationElements.forEach(element => {
            element.style.display = '';
        });
    },
    
    showToast: function(type, message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000,
                icon: type,
                title: message
            });
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
};

// Auto-inicialización
function initUnifiedSearch() {
    const currentPath = window.location.pathname;
    let moduleName = null;
    
    if (currentPath.includes('/technical_service') || currentPath.includes('/create_ticket') || currentPath.includes('/edit_ticket')) {
        moduleName = 'technical_service';
    } else if (currentPath.includes('/internal_repair') || currentPath.includes('/create_ticketsRI') || currentPath.includes('/edit_tickets_RI')) {
        moduleName = 'internal_repair';
    } else if (currentPath.includes('/warranty') || currentPath.includes('/create_warranty') || currentPath.includes('/edit_warranty')) {
        moduleName = 'warranty';
    } else if (currentPath.includes('/view_technical')) {
        moduleName = 'view_technical';
    }
    
    if (moduleName) {
        UnifiedSearch.init(moduleName);
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUnifiedSearch);
} else {
    initUnifiedSearch();
}
