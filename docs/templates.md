# Documentación - Módulo Templates

## 📋 Información General

**Módulo:** `apps.tickets.templates`  
**Propósito:** Plantillas HTML y componentes de interfaz de usuario  
**Ubicación:** `apps/tickets/templates/`  

## 🏗️ Arquitectura de Vistas

### Template Engine
- **Motor:** Jinja2 (Flask integrado)
- **Herencia:** Template base reutilizable
- **Componentes:** Partials modulares
- **Frontend:** Bootstrap 5 + JavaScript vanilla

### Estructura de Templates
```
templates/
├── base.html                    # Template base
├── dashboard.html               # Panel principal
├── technical_service.html       # Lista ST
├── internal_repair.html         # Lista RI
├── warranty.html                # Lista GA
├── create_ticket.html           # Crear ticket ST
├── create_ticketsRI.html        # Crear ticket RI
├── create_warranty.html         # Crear garantía
├── edit_ticket.html             # Editar ticket ST
├── edit_tickets_RI.html         # Editar ticket RI
├── edit_warranty.html           # Editar garantía
├── view_detail_ticket.html      # Detalle ticket ST
├── detail_RI.html               # Detalle ticket RI
├── view_detail_warranty.html    # Detalle garantía
├── view_technical.html          # Vista técnico ST
├── view_technicalRI.html        # Vista técnico RI
├── technician_ticket_detail.html # Detalle móvil ST
├── technician_ticketRI_detail.html # Detalle móvil RI
├── upload_images.html           # Carga de imágenes
├── login.html                   # Autenticación
├── index.html                   # Página principal
├── detail_modal.html            # Modal de detalles
└── partials/                    # Componentes reutilizables
    ├── internal_repair_table_rows.html
    ├── tickets_table_rows.html
    ├── view_technical_table_rows.html
    └── warranty_table_rows.html
```

## 🎨 Plantillas Principales

### 1. Base Template (`base.html`)

#### Propósito
Template base que define la estructura común de todas las páginas.

#### Características
- **Layout responsivo** con Bootstrap 5
- **Navegación consistente**
- **Gestión de assets** (CSS/JS)
- **Bloques extensibles**

#### Estructura
```html
<!DOCTYPE html>
<html lang="es">
<head>
    {% block head %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sistema de Tickets{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    {% block styles %}{% endblock %}
    {% endblock %}
</head>
<body>
    {% block navbar %}
    <!-- Navegación principal -->
    {% endblock %}
    
    <main class="container-fluid">
        {% block content %}{% endblock %}
    </main>
    
    {% block scripts %}
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- SweetAlert2 -->
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.7.12/dist/sweetalert2.all.min.js"></script>
    {% endblock %}
</body>
</html>
```

#### Bloques Disponibles
- `head`: Metadatos y recursos
- `title`: Título de la página
- `styles`: CSS adicional
- `navbar`: Navegación (si se requiere personalización)
- `content`: Contenido principal
- `scripts`: JavaScript adicional

### 2. Dashboard (`dashboard.html`)

#### Propósito
Panel de control principal con métricas y análisis de datos.

#### Características
- **KPIs en tiempo real**
- **Gráficos interactivos** (Chart.js)
- **Tablas paginadas**
- **Filtros temporales**
- **Responsive design**

#### Componentes Principales

##### Controles de Período
```html
<div class="controls-section mb-5">
    <div class="period-selector">
        <div class="period-buttons" id="date-range-selector">
            <button class="period-btn active" data-period="today">Hoy</button>
            <button class="period-btn" data-period="week">Semana</button>
            <button class="period-btn" data-period="month">Mes</button>
            <button class="period-btn" data-period="year">Año</button>
            <button class="period-btn" data-period="all">Todo</button>
        </div>
    </div>
</div>
```

##### KPI Cards
```html
<div class="kpi-card kpi-tickets">
    <div class="card-body">
        <div class="kpi-icon-container">
            <i class="fa fa-ticket-alt kpi-icon"></i>
        </div>
        <div class="kpi-content">
            <h6 class="kpi-title">Tickets Activos</h6>
            <span class="kpi-value" id="kpi-active-tickets">--</span>
        </div>
    </div>
</div>
```

##### Gráficos
```html
<div class="chart-container">
    <canvas id="chart-tickets-technician" height="120"></canvas>
</div>
```

##### Tabla de Tickets Pendientes
```html
<table class="modern-table" id="pending-tickets-table">
    <thead class="modern-table-header">
        <tr>
            <th>ID</th>
            <th>Documento</th>
            <th>Producto</th>
            <th>Estado</th>
            <th>Técnico</th>
            <th>Ciudad</th>
            <th>Tiempo</th>
            <th>Prioridad</th>
            <th>Tipo</th>
        </tr>
    </thead>
    <tbody id="pending-tickets-body">
        <!-- Contenido dinámico -->
    </tbody>
</table>
```

### 3. Formularios de Creación

#### Create Ticket (`create_ticket.html`)
Formulario completo para crear tickets de servicio técnico.

##### Secciones del Formulario
```html
<!-- Información del Cliente -->
<div class="form-section">
    <h4>Información del Cliente</h4>
    <input type="text" name="document_client" placeholder="Documento" required>
    <input type="text" name="client_name" placeholder="Nombre completo">
</div>

<!-- Información del Producto -->
<div class="form-section">
    <h4>Información del Producto</h4>
    <input type="text" name="product_code" placeholder="Código del producto" required>
    <input type="text" name="IMEI" placeholder="IMEI" required>
    <input type="text" name="reference" placeholder="Referencia">
</div>

<!-- Problemas Detectados -->
<div class="form-section">
    <h4>Problemas Detectados</h4>
    <div class="problems-grid" id="problems-container">
        <!-- Checkboxes dinámicos -->
    </div>
</div>

<!-- Información del Servicio -->
<div class="form-section">
    <h4>Información del Servicio</h4>
    <select name="priority" required>
        <option value="Alta">Alta</option>
        <option value="Media">Media</option>
        <option value="Baja">Baja</option>
    </select>
    <select name="technical_document" required>
        <!-- Técnicos disponibles -->
    </select>
</div>
```

#### Create Warranty (`create_warranty.html`)
Formulario especializado para garantías.

##### Campos Específicos
```html
<!-- Información de Garantía -->
<div class="warranty-section">
    <input type="text" name="original_invoice" placeholder="Factura original">
    <input type="date" name="purchase_date" placeholder="Fecha de compra">
    <textarea name="warranty_reason" placeholder="Motivo de garantía"></textarea>
</div>
```

### 4. Formularios de Edición

#### Edit Ticket (`edit_ticket.html`)
Formulario para editar tickets existentes con datos precargados.

##### Características
- **Datos precargados** del ticket
- **Validación en tiempo real**
- **Campos deshabilitados** según estado
- **Historial de cambios**

```html
<form id="edit-ticket-form" data-ticket-id="{{ ticket.id_ticket }}">
    <!-- Campos editables según el estado -->
    {% if ticket.state != 'Terminado' %}
        <input type="text" name="reference" value="{{ ticket.reference }}">
    {% else %}
        <input type="text" value="{{ ticket.reference }}" readonly>
    {% endif %}
</form>
```

### 5. Vistas de Detalle

#### Ticket Detail (`view_detail_ticket.html`)
Vista completa de un ticket con toda su información.

##### Secciones
```html
<!-- Header del Ticket -->
<div class="ticket-header">
    <h2>Ticket #{{ ticket.id_ticket }}</h2>
    <span class="badge badge-{{ ticket.state }}">{{ ticket.state }}</span>
</div>

<!-- Información Principal -->
<div class="ticket-info">
    <div class="info-grid">
        <div class="info-item">
            <label>Cliente:</label>
            <span>{{ ticket.document_client }}</span>
        </div>
        <!-- Más campos... -->
    </div>
</div>

<!-- Problemas Asociados -->
<div class="problems-section">
    <h4>Problemas Detectados</h4>
    <ul class="problems-list">
        {% for problem in ticket.problems %}
            <li>{{ problem.name }}</li>
        {% endfor %}
    </ul>
</div>

<!-- Repuestos Utilizados -->
<div class="spares-section">
    <h4>Repuestos</h4>
    <table class="spares-table">
        {% for spare in spare_parts %}
            <tr>
                <td>{{ spare.name }}</td>
                <td>{{ spare.quantity }}</td>
                <td>${{ spare.price }}</td>
            </tr>
        {% endfor %}
    </table>
</div>
```

### 6. Vistas de Lista

#### Technical Service (`technical_service.html`)
Lista de tickets de servicio técnico con filtros y paginación.

##### Características
- **Filtros avanzados**
- **Búsqueda en tiempo real**
- **Paginación AJAX**
- **Ordenamiento por columnas**

```html
<!-- Controles de Filtro -->
<div class="filters-section">
    <input type="text" id="search-input" placeholder="Buscar...">
    <select id="state-filter">
        <option value="">Todos los estados</option>
        <option value="Sin asignar">Sin asignar</option>
        <option value="Asignado">Asignado</option>
    </select>
</div>

<!-- Tabla de Tickets -->
<table class="tickets-table" id="tickets-table">
    <thead>
        <tr>
            <th data-sort="id_ticket">ID</th>
            <th data-sort="document_client">Cliente</th>
            <th data-sort="state">Estado</th>
            <th data-sort="priority">Prioridad</th>
            <th>Acciones</th>
        </tr>
    </thead>
    <tbody id="tickets-body">
        <!-- Contenido dinámico via AJAX -->
    </tbody>
</table>

<!-- Paginación -->
<nav class="pagination-nav">
    <ul class="pagination" id="pagination-controls">
        <!-- Controles dinámicos -->
    </ul>
</nav>
```

### 7. Vistas Móviles

#### Technician Detail (`technician_ticket_detail.html`)
Vista optimizada para técnicos en dispositivos móviles.

##### Características
- **Diseño mobile-first**
- **Navegación táctil**
- **Información condensada**
- **Acciones rápidas**

```html
<div class="mobile-ticket-card">
    <div class="card-header">
        <span class="ticket-id">#{{ ticket.id_ticket }}</span>
        <span class="ticket-status">{{ ticket.state }}</span>
    </div>
    
    <div class="card-body">
        <div class="client-info">
            <i class="fa fa-user"></i>
            <span>{{ ticket.document_client }}</span>
        </div>
        
        <div class="product-info">
            <i class="fa fa-mobile"></i>
            <span>{{ ticket.reference }}</span>
        </div>
    </div>
    
    <div class="card-actions">
        <button class="btn-action" onclick="updateStatus('En proceso')">
            Iniciar
        </button>
        <button class="btn-action" onclick="viewDetails()">
            Ver Más
        </button>
    </div>
</div>
```

## 🎯 Componentes Reutilizables

### 1. Partials

#### Table Rows (`partials/tickets_table_rows.html`)
Filas de tabla reutilizables para diferentes vistas.

```html
{% for ticket in tickets %}
<tr class="ticket-row" data-ticket-id="{{ ticket.id_ticket }}">
    <td class="ticket-id">#{{ ticket.id_ticket }}</td>
    <td class="client-doc">{{ ticket.document_client }}</td>
    <td class="product-ref">{{ ticket.reference }}</td>
    <td class="ticket-state">
        <span class="badge badge-{{ ticket.state|lower|replace(' ', '-') }}">
            {{ ticket.state }}
        </span>
    </td>
    <td class="ticket-priority">
        <span class="priority priority-{{ ticket.priority|lower }}">
            {{ ticket.priority }}
        </span>
    </td>
    <td class="ticket-actions">
        <button class="btn-sm btn-outline-primary" onclick="viewTicket({{ ticket.id_ticket }})">
            <i class="fa fa-eye"></i>
        </button>
        <button class="btn-sm btn-outline-warning" onclick="editTicket({{ ticket.id_ticket }})">
            <i class="fa fa-edit"></i>
        </button>
    </td>
</tr>
{% endfor %}
```

### 2. Modales

#### Detail Modal (`detail_modal.html`)
Modal reutilizable para mostrar detalles rápidos.

```html
<div class="modal fade" id="detailModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Detalles del Ticket</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="modal-content">
                <!-- Contenido dinámico -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    Cerrar
                </button>
            </div>
        </div>
    </div>
</div>
```

## 🎨 Estilos y Diseño

### Sistema de Colores
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --info-color: #3b82f6;
    --light-color: #f8fafc;
    --dark-color: #1e293b;
}
```

### Componentes Modernos
- **Cards con sombras suaves**
- **Botones con estados hover**
- **Formularios con validación visual**
- **Tablas con ordenamiento**
- **Badges con colores semánticos**

### Responsive Design
```css
/* Mobile First */
@media (max-width: 767px) {
    .desktop-only { display: none; }
    .mobile-stack { flex-direction: column; }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1024px) {
    .tablet-hide { display: none; }
}

/* Desktop */
@media (min-width: 1025px) {
    .mobile-only { display: none; }
}
```

## 🔧 JavaScript Interactivo

### Funcionalidades AJAX
- **Carga de datos sin recarga**
- **Filtros en tiempo real**
- **Paginación dinámica**
- **Actualización de estados**

### Validación de Formularios
```javascript
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required]');
    
    let isValid = true;
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}
```

### Notificaciones
```javascript
function showNotification(title, text, icon = 'success') {
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000
    });
}
```

## 📱 Accesibilidad

### Estándares WCAG
- **Contraste de colores** adecuado
- **Navegación por teclado**
- **Etiquetas semánticas**
- **Textos alternativos**

### Implementación
```html
<!-- Etiquetas semánticas -->
<main role="main">
    <section aria-labelledby="tickets-heading">
        <h2 id="tickets-heading">Lista de Tickets</h2>
        <!-- Contenido -->
    </section>
</main>

<!-- Navegación accesible -->
<nav aria-label="Paginación de tickets">
    <ul class="pagination">
        <li><a href="#" aria-label="Página anterior">«</a></li>
        <li><a href="#" aria-current="page">1</a></li>
    </ul>
</nav>
```

---

*Documentación del módulo Templates - Sistema de Tickets v2.1.0* 