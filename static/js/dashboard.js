// dashboard.js
// Lógica principal del dashboard: KPIs, gráficos, tablas y paginación
// Usa fetch, Chart.js, SweetAlert2 y Bootstrap 5

// ==================== CONFIGURACIÓN ====================
const ENDPOINTS = {
    metrics: '/tickets/dashboard/metrics',
    ticketsByTechnician: '/tickets/dashboard/tickets-by-technician',
    ticketsDistribution: '/tickets/dashboard/tickets-distribution',
    timeline: '/tickets/dashboard/timeline-data',
    pendingTickets: '/tickets/dashboard/pending-tickets',
    topProblems: '/tickets/dashboard/top-problems'
};

let currentPeriod = 'today';
let customStart = null;
let customEnd = null;
let pendingPage = 1;
let pendingPerPage = 10;
let techPage = 1;
let techPerPage = 10;
let problemsPage = 1;
let problemsPerPage = 5;

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    setupDateRangeSelector();
    // Establecer layout inicial según período por defecto
    updateLayoutForPeriod();
    loadDashboard();
    setupExportBtn();
});

// ==================== FUNCIONES PRINCIPALES ====================
function loadDashboard() {
    loadKPIs();
    loadTicketsByTechnician();
    loadTicketsDistribution();
    loadTopProblems();
    
    // Controlar visibilidad de sección temporal según período
    updateLayoutForPeriod();
    
    // Cargar timeline solo si no es "today"
    if (currentPeriod !== 'today') {
        loadTimeline();
    }
    
    loadPendingTickets();
}

// ---------- KPIs ----------
function loadKPIs() {
    // Mostrar estado de carga
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach(card => card.classList.add('loading'));
    
    fetch(buildUrl(ENDPOINTS.metrics))
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                // Valores básicos
                document.getElementById('kpi-active-tickets').textContent = res.data.active_tickets || '0';
                document.getElementById('kpi-avg-time').textContent = (res.data.avg_resolution_time_hours || 0) + ' horas';
                document.getElementById('kpi-active-warranties').textContent = res.data.active_warranties || '0';
                
                // Valores facturados - asegurar que no sean undefined/null
                const facturedST = res.data.facturado_st || 0;
                const facturedRI = res.data.facturado_ri || 0;
                
                document.getElementById('kpi-facturado-st').textContent = '$' + numberFormat(facturedST);
                document.getElementById('kpi-facturado-ri').textContent = '$' + numberFormat(facturedRI);
                
                // Actualizar tendencias y porcentajes si están disponibles
                if (res.data.trends) {
                    updateKPITrends(res.data.trends);
                }
                
                // Animar los valores con efecto contador
                animateKPIValues();
                
                // Solo mostrar toast si hay un mensaje específico o si es la primera carga
                if (res.message && res.message.title !== '¡Datos cargados!') {
                    showSwal(res.message);
                }
            }
        })
        .catch(err => {
            console.error('Error loading KPIs:', err);
            // Mostrar valores por defecto en caso de error
            document.getElementById('kpi-active-tickets').textContent = '--';
            document.getElementById('kpi-avg-time').textContent = '-- horas';
            document.getElementById('kpi-active-warranties').textContent = '--';
            document.getElementById('kpi-facturado-st').textContent = '$--';
            document.getElementById('kpi-facturado-ri').textContent = '$--';
            showErrorAlert('Error', 'No se pudo cargar KPIs');
        })
        .finally(() => {
            // Remover estado de carga
            setTimeout(() => {
                kpiCards.forEach(card => card.classList.remove('loading'));
            }, 500);
        });
}

// Función para animar los valores KPI con efecto contador
function animateKPIValues() {
    const kpiValues = document.querySelectorAll('.kpi-value, .kpi-value-small');
    kpiValues.forEach(element => {
        const text = element.textContent;
        if (text && text !== '--' && !text.includes('$') && !text.includes('horas')) {
            const finalValue = parseInt(text) || 0;
            if (finalValue > 0) {
                animateCounter(element, 0, finalValue, 1000);
            }
        }
    });
}

// Función auxiliar para animar contadores
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        if (current === end) {
            clearInterval(timer);
        }
    }, stepTime);
}

// ---------- Tickets por técnico (gráfico de barras) ----------
let chartTech = null;
function loadTicketsByTechnician() {
    fetch(buildUrl(ENDPOINTS.ticketsByTechnician, { page: techPage, per_page: techPerPage, period: currentPeriod }))
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                const labels = res.data.map(t => t.technician);
                const data = res.data.map(t => t.ticket_count);
                renderBarChart('chart-tickets-technician', labels, data, 'Tickets por técnico', chart => chartTech = chart, chartTech);
            }
            // No swal para cada paginación
        });
}

// ---------- Distribución de tickets (gráfico de torta) ----------
let chartDist = null;
function loadTicketsDistribution() {
    fetch(buildUrl(ENDPOINTS.ticketsDistribution, { period: currentPeriod, group_by: 'type_of_service' }))
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                // Traducir etiquetas si vienen como 0,1,2
                const typeLabels = { "0": "ST", "1": "RI", "2": "GA", "ST": "ST", "RI": "RI", "GA": "GA" };
                const labels = res.data.map(d => typeLabels[d.label] || d.label);
                const data = res.data.map(d => d.value);
                renderPieChart('chart-tickets-distribution', labels, data, chart => chartDist = chart, chartDist);
            }
        });
}

// ---------- Timeline (gráfico de línea) ----------
let chartTimeline = null;
function loadTimeline() {
    fetch(buildUrl(ENDPOINTS.timeline, { period: currentPeriod }))  // Remover granularity fija
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                const labels = res.data.map(d => d.period);
                const data = res.data.map(d => d.total_tickets);
                renderLineChart('chart-timeline', labels, data, chart => chartTimeline = chart, chartTimeline);
                
                // Opcional: mostrar información sobre la granularidad usada
                if (res.granularity && res.days_range) {
                    console.log(`Timeline: ${res.granularity} para ${res.days_range} días`);
                }
            }
        });
}

// ---------- Tickets pendientes (tabla paginada) ----------
function loadPendingTickets() {
    fetch(buildUrl(ENDPOINTS.pendingTickets, { page: pendingPage, per_page: pendingPerPage }))
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                renderPendingTicketsTable(res.data);
                renderPagination('pending-tickets-pagination', res.pagination, page => {
                    pendingPage = page;
                    loadPendingTickets();
                });
            } else {
                console.error('Error en la respuesta de tickets pendientes:', res);
            }
        })
        .catch(error => {
            console.error('Error cargando tickets pendientes:', error);
        });
}
function renderPendingTicketsTable(items) {
    const tbody = document.getElementById('pending-tickets-body');
    tbody.innerHTML = '';
    
    if (!items.length) {
        tbody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9" class="loading-cell">
                    <div class="loading-content">
                        <i class="fa fa-inbox fa-2x text-muted"></i>
                        <span>Sin tickets pendientes</span>
                    </div>
                </td>
            </tr>`;
        return;
    }
    
    for (const t of items) {
        const stateBadgeClass = getModernBadgeClass(t.state, 'state');
        const priorityBadgeClass = getModernBadgeClass(t.priority, 'priority');
        const serviceTypeBadgeClass = getModernBadgeClass(t.service_type, 'service_type');
        
        tbody.innerHTML += `
            <tr class="ticket-row" data-ticket-id="${t.id}">
                <td class="d-none d-md-table-cell">
                    <span class="fw-bold text-primary">#${t.id}</span>
                </td>
                <td class="text-truncate" title="${t.document}">
                    <div class="d-flex align-items-center">
                        <i class="fa fa-id-card fa-sm me-2 text-muted d-none d-lg-inline"></i>
                        <span class="fw-bold">${t.document}</span>
                    </div>
                </td>
                <td class="d-none d-md-table-cell text-truncate" title="${t.product}">
                    <small class="text-muted">${t.product}</small>
                </td>
                <td>
                    <span class="modern-badge ${stateBadgeClass}">${t.state}</span>
                </td>
                <td class="d-none d-lg-table-cell text-truncate" title="${t.technician}">
                    <div class="d-flex align-items-center">
                        <i class="fa fa-tools fa-sm me-2 text-muted"></i>
                        <span>${t.technician}</span>
                    </div>
                </td>
                <td class="d-none d-md-table-cell text-truncate" title="${t.city}">
                    <div class="d-flex align-items-center">
                        <i class="fa fa-map-marker-alt fa-sm me-2 text-muted"></i>
                        <small class="text-muted">${t.city}</small>
                    </div>
                </td>
                <td class="d-none d-md-table-cell">
                    <small class="text-muted">${t.waiting_time}</small>
                </td>
                <td>
                    <span class="modern-badge ${priorityBadgeClass}">${t.priority}</span>
                </td>
                <td class="d-none d-md-table-cell">
                    <span class="modern-badge ${serviceTypeBadgeClass}">${t.service_type}</span>
                </td>
            </tr>`;
    }
}

// ---------- Top problemas (lista paginada) ----------
function loadTopProblems() {
    fetch(buildUrl(ENDPOINTS.topProblems, { page: problemsPage, per_page: problemsPerPage, period: currentPeriod }))
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                renderTopProblemsList(res.data);
                renderPagination('top-problems-pagination', res.pagination, page => {
                    problemsPage = page;
                    loadTopProblems();
                });
            }
        });
}
function renderTopProblemsList(items) {
    const ul = document.getElementById('top-problems-list');
    ul.innerHTML = '';
    
    if (!items.length) {
        ul.innerHTML = `
            <li class="loading-item">
                <div class="loading-content">
                    <i class="fa fa-exclamation-circle text-muted"></i>
                    <span>Sin problemas frecuentes</span>
                </div>
            </li>`;
        return;
    }
    
    for (const p of items) {
        ul.innerHTML += `
            <li>
                <div class="problem-info">
                    <span class="problem-title">${p.problem}</span>
                    <small class="text-muted">Casos reportados</small>
                </div>
                <span class="modern-badge badge-danger">${p.count}</span>
            </li>`;
    }
}

// ==================== UTILIDADES ====================
function buildUrl(base, params = {}) {
    let url = base + '?';
    if (currentPeriod !== 'custom') params.period = currentPeriod;
    if (currentPeriod === 'custom' && customStart && customEnd) {
        params.start_date = customStart;
        params.end_date = customEnd;
    }
    return url + Object.entries(params).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
}
function numberFormat(n) {
    return n.toLocaleString('es-CO', { minimumFractionDigits: 0 });
}
function stateColor(state) {
    if (state === 'En proceso') return 'warning';
    if (state === 'Asignado') return 'info';
    if (state === 'Sin asignar') return 'secondary';
    if (state === 'Terminado') return 'success';
    return 'primary';
}
function priorityColor(priority) {
    if (priority === 'Alta') return 'danger';
    if (priority === 'Media') return 'warning';
    return 'success';
}
function showSwal(msg) {
    if (!msg) return;
    
    // Mostrar alerta modal como antes
    Swal.fire({
        icon: msg.icon || 'info',
        title: msg.title || 'Notificación',
        text: msg.text || '',
        confirmButtonText: 'Aceptar'
    });
}

// Funciones auxiliares para alertas específicas
function showSuccessAlert(title, text = '') {
    showSwal({ icon: 'success', title, text });
}

function showErrorAlert(title, text = '') {
    showSwal({ icon: 'error', title, text });
}

function showWarningAlert(title, text = '') {
    showSwal({ icon: 'warning', title, text });
}

function showInfoAlert(title, text = '') {
    showSwal({ icon: 'info', title, text });
}

// ==================== CHARTS ====================
function renderBarChart(id, labels, data, label, setChart, oldChart) {
    if (oldChart) oldChart.destroy();
    const ctx = document.getElementById(id).getContext('2d');
    
    // Configuración responsive
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth < 1200;
    
    setChart(new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data,
                backgroundColor: '#0d6efd',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: isMobile ? 90 : (isTablet ? 45 : 0),
                        font: {
                            size: isMobile ? 10 : (isTablet ? 11 : 12)
                        }
                    }
                },
                y: {
                    ticks: {
                        font: {
                            size: isMobile ? 10 : (isTablet ? 11 : 12)
                        }
                    }
                }
            }
        }
    }));
}
function renderPieChart(id, labels, data, setChart, oldChart) {
    if (oldChart) oldChart.destroy();
    const ctx = document.getElementById(id).getContext('2d');
    
    // Configuración responsive
    const isMobile = window.innerWidth < 768;
    
    setChart(new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: [
                    '#0d6efd', '#20c997', '#ffc107', '#dc3545', '#6c757d', '#6610f2', '#fd7e14'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { 
                    position: isMobile ? 'bottom' : 'right',
                    labels: {
                        font: {
                            size: isMobile ? 10 : 12
                        },
                        padding: isMobile ? 10 : 20
                    }
                }
            }
        }
    }));
}
function renderLineChart(id, labels, data, setChart, oldChart) {
    if (oldChart) oldChart.destroy();
    const ctx = document.getElementById(id).getContext('2d');
    
    // Configuración mejorada para timeline con muchos datos
    const maxDisplayLabels = 20;
    const shouldSkipLabels = labels.length > maxDisplayLabels;
    
    setChart(new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Tickets',
                data,
                fill: true,  // Área bajo la línea
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.3,
                pointRadius: shouldSkipLabels ? 1 : 3,  // Puntos más pequeños si hay muchos datos
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Período: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `${context.parsed.y} tickets`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        maxTicksLimit: maxDisplayLabels,
                        callback: function(value, index) {
                            // Si hay muchas etiquetas, mostrar solo algunas
                            if (shouldSkipLabels) {
                                const step = Math.ceil(labels.length / maxDisplayLabels);
                                return index % step === 0 ? this.getLabelForValue(value) : '';
                            }
                            return this.getLabelForValue(value);
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    }));
}

// ==================== PAGINACIÓN ====================
function renderPagination(containerId, pagination, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container || !pagination) return;

    const { page, pages, has_prev, has_next } = pagination;
    
    if (pages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHTML = '<div class="modern-pagination">';
    
    // Botón anterior
    paginationHTML += `
        <button class="page-btn ${!has_prev ? 'disabled' : ''}" 
                onclick="${has_prev ? `(${onPageChange})(${page - 1})` : 'void(0)'}"
                ${!has_prev ? 'disabled' : ''}>
            <i class="fa fa-chevron-left"></i>
        </button>`;
    
    // Números de página
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(pages, page + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <button class="page-btn" onclick="(${onPageChange})(1)">1</button>`;
        if (startPage > 2) {
            paginationHTML += '<span class="page-dots">...</span>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <button class="page-btn ${i === page ? 'active' : ''}" 
                    onclick="(${onPageChange})(${i})">${i}</button>`;
    }
    
    if (endPage < pages) {
        if (endPage < pages - 1) {
            paginationHTML += '<span class="page-dots">...</span>';
        }
        paginationHTML += `
            <button class="page-btn" onclick="(${onPageChange})(${pages})">${pages}</button>`;
    }
    
    // Botón siguiente
    paginationHTML += `
        <button class="page-btn ${!has_next ? 'disabled' : ''}" 
                onclick="${has_next ? `(${onPageChange})(${page + 1})` : 'void(0)'}"
                ${!has_next ? 'disabled' : ''}>
            <i class="fa fa-chevron-right"></i>
        </button>`;
    
    paginationHTML += '</div>';
    container.innerHTML = paginationHTML;
}

// ==================== SELECTOR DE FECHAS ====================
function setupDateRangeSelector() {
    // Manejar botones de período moderno
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPeriod = btn.getAttribute('data-period');
            if (currentPeriod !== 'custom') {
                document.getElementById('custom-range-picker').classList.add('d-none');
                loadDashboard();
            }
        });
    });

    // Botón de rango personalizado
    document.getElementById('custom-range-btn').addEventListener('click', () => {
        const container = document.getElementById('custom-range-picker');
        container.classList.toggle('d-none');
        
        if (!container.classList.contains('d-none')) {
            // Auto-focus en el primer input
            setTimeout(() => {
                document.getElementById('start-date').focus();
            }, 100);
        }
    });

    // Aplicar rango personalizado
    document.getElementById('apply-custom-range').addEventListener('click', () => {
        const start = document.getElementById('start-date').value;
        const end = document.getElementById('end-date').value;
        
        if (start && end) {
            if (new Date(start) > new Date(end)) {
                showWarningAlert('Fechas inválidas', 'La fecha de inicio debe ser anterior a la fecha de fin');
                return;
            }
            
            customStart = start;
            customEnd = end;
            currentPeriod = 'custom';
            document.getElementById('custom-range-picker').classList.add('d-none');
            
            // Actualizar indicador visual del período personalizado
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('custom-range-btn').classList.add('active');
            
            loadDashboard();
            showSuccessAlert('Rango aplicado', `Datos desde ${start} hasta ${end}`);
        } else {
            showWarningAlert('Fechas incompletas', 'Por favor selecciona ambas fechas');
        }
    });
}

// ==================== EXPORTAR ====================
function setupExportBtn() {
    document.getElementById('export-btn').addEventListener('click', () => {
        showInfoAlert('Función de exportar', 'Esta funcionalidad estará disponible próximamente');
    });
}

// ==================== FUNCIONES ADICIONALES PARA TABLETS ====================

// Función removida: setupRefreshBtn() ya que se quitó el botón de actualizar

// Función para ver detalles de ticket
function viewTicket(ticketId) {
    showInfoAlert('Ver Ticket', `Abriendo detalles del ticket #${ticketId}`);
    // Aquí se podría abrir un modal o redirigir a la página de detalles
}

// Función para cancelar selector de fechas personalizado
function setupCancelCustomRange() {
    const cancelBtn = document.getElementById('cancel-custom-range');
    const customPicker = document.getElementById('custom-range-picker');
    const customBtn = document.getElementById('custom-range-btn');
    
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            customPicker.classList.add('d-none');
            customBtn.classList.remove('active');
            // Limpiar campos
            document.getElementById('start-date').value = '';
            document.getElementById('end-date').value = '';
            
            // Reactivar el período anterior
            const activeBtn = document.querySelector('#date-range-selector .btn.active');
            if (!activeBtn) {
                document.querySelector('#date-range-selector .btn[data-period="today"]').classList.add('active');
                currentPeriod = 'today';
                loadDashboard();
            }
        });
    }
}

// Inicializar funciones adicionales
document.addEventListener('DOMContentLoaded', () => {
    setupCancelCustomRange();
    setupChartResizeHandler();
});

// Función para manejar redimensionamiento de gráficos
function setupChartResizeHandler() {
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            // Redimensionar gráficos después de cambio de orientación/tamaño
            if (chartTech) chartTech.resize();
            if (chartDist) chartDist.resize();
            if (chartTimeline) chartTimeline.resize();
        }, 250);
    });
    
    // Manejar cambio de orientación específicamente en tablets/móviles
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            if (chartTech) chartTech.resize();
            if (chartDist) chartDist.resize();
            if (chartTimeline) chartTimeline.resize();
        }, 500); // Dar tiempo para que se complete el cambio de orientación
    });
}

// Función para actualizar tendencias de KPIs con datos reales
function updateKPITrends(trends) {
    const kpiMappings = [
        { kpi: 'active_tickets', id: 'kpi-tickets' },
        { kpi: 'avg_resolution_time_hours', id: 'kpi-time' },
        { kpi: 'active_warranties', id: 'kpi-warranties' },
        { kpi: 'facturado_st', id: 'kpi-revenue-st' },
        { kpi: 'facturado_ri', id: 'kpi-revenue-ri' }
    ];

    kpiMappings.forEach(({ kpi, id }) => {
        const trendElement = document.getElementById(id);
        if (!trendElement) return;

        const changeKey = `${kpi}_change`;
        const directionKey = `${kpi}_direction`;
        
        if (trends && trends[changeKey] !== undefined) {
            const change = Math.abs(trends[changeKey]);
            const direction = trends[directionKey];
            
            // Solo mostrar porcentaje si es significativo (> 0.1%)
            if (change >= 0.1) {
                // Actualizar icono y texto de tendencia
                const icon = direction === 'up' ? 'fa-arrow-up' : 
                            direction === 'down' ? 'fa-arrow-down' : 'fa-minus';
                const colorClass = direction === 'up' ? 'trend-up' : 
                                  direction === 'down' ? 'trend-down' : 'trend-neutral';
                
                // Determinar si es kpi-trend o kpi-trend-small
                const isSmall = trendElement.classList.contains('kpi-trend-small');
                trendElement.className = isSmall ? `kpi-trend-small ${colorClass}` : `kpi-trend ${colorClass}`;
                
                const prefix = direction === 'up' ? '+' : direction === 'down' ? '-' : '';
                trendElement.innerHTML = `
                    <i class="fa ${icon} ${isSmall ? 'fa-xs' : 'fa-sm'}"></i>
                    <span class="small">${prefix}${change.toFixed(1)}%</span>
                `;
            } else {
                // Cambio muy pequeño, mostrar como neutral
                const isSmall = trendElement.classList.contains('kpi-trend-small');
                trendElement.className = isSmall ? 'kpi-trend-small trend-neutral' : 'kpi-trend trend-neutral';
                trendElement.innerHTML = `
                    <i class="fa fa-minus ${isSmall ? 'fa-xs' : 'fa-sm'}"></i>
                    <span class="small">Sin cambios</span>
                `;
            }
        } else {
            // No hay datos de tendencia disponibles
            const isSmall = trendElement.classList.contains('kpi-trend-small');
            trendElement.className = isSmall ? 'kpi-trend-small trend-neutral' : 'kpi-trend trend-neutral';
            trendElement.innerHTML = `
                <i class="fa fa-minus ${isSmall ? 'fa-xs' : 'fa-sm'}"></i>
                <span class="small">--</span>
            `;
        }

        // Actualizar barra de progreso si existe
        const progressBar = trendElement.closest('.kpi-card').querySelector('.progress-bar');
        if (progressBar && trends && trends[changeKey] !== undefined) {
            // Usar un valor basado en el porcentaje, pero limitado para la visualización
            const progressValue = Math.min(Math.max(Math.abs(trends[changeKey] || 0), 10), 100);
            progressBar.style.width = `${progressValue}%`;
        }
    });
}

// Función para obtener clases modernas de badges
function getModernBadgeClass(value, type) {
    if (type === 'state') {
        const stateClasses = {
            'En proceso': 'badge-warning',
            'Asignado': 'badge-info',
            'Sin asignar': 'badge-secondary',
            'Terminado': 'badge-success',
            'En Revision': 'badge-info'
        };
        return stateClasses[value] || 'badge-secondary';
    }
    
    if (type === 'priority') {
        const priorityClasses = {
            'Alta': 'badge-danger',
            'Media': 'badge-warning',
            'Baja': 'badge-success'
        };
        return priorityClasses[value] || 'badge-secondary';
    }
    
    if (type === 'service_type') {
        const serviceTypeClasses = {
            'ST': 'badge-info',        // Servicio Técnico - azul
            'RI': 'badge-warning',     // Reparación Interna - amarillo
            'GA': 'badge-success',     // Garantía - verde
            'N/A': 'badge-secondary'   // No disponible - gris
        };
        return serviceTypeClasses[value] || 'badge-secondary';
    }
    
    return 'badge-secondary';
}

// Nueva función para controlar el layout según el período
function updateLayoutForPeriod() {
    const timelineSection = document.getElementById('timeline-section');
    
    if (currentPeriod === 'today') {
        // Para "HOY": ocultar timeline con transición suave
        if (timelineSection.style.display !== 'none') {
            timelineSection.classList.add('hide');
            setTimeout(() => {
                timelineSection.style.display = 'none';
                timelineSection.classList.remove('hide');
            }, 300);
        }
    } else {
        // Para otros períodos: mostrar timeline con transición suave
        if (timelineSection.style.display === 'none') {
            timelineSection.style.display = 'block';
            timelineSection.classList.add('show');
            setTimeout(() => {
                timelineSection.classList.remove('show');
            }, 300);
        }
    }
    
    // Agregar indicador visual de transición
    const chartsSection = document.querySelector('.charts-section');
    const dataSection = document.querySelector('.data-section');
    
    chartsSection?.classList.add('period-transition');
    dataSection?.classList.add('period-transition');
    
    setTimeout(() => {
        chartsSection?.classList.remove('period-transition');
        dataSection?.classList.remove('period-transition');
    }, 200);
    
    // Debug: mostrar información del layout en consola
    console.log(`Layout actualizado para período: ${currentPeriod}`, {
        timelineVisible: timelineSection.style.display !== 'none',
        period: currentPeriod
    });
} 