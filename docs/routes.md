# Documentación - Módulo Routes

## 📋 Información General

**Módulo:** `apps.tickets.routes`  
**Propósito:** Controladores HTTP y definición de endpoints  
**Ubicación:** `apps/tickets/routes/`  

## 🏗️ Arquitectura de Rutas

### Patrón Blueprint
- **Blueprint Principal:** `tickets`
- **Sub-blueprints:** Por funcionalidad específica
- **Prefijo de URL:** `/tickets`
- **Control de Acceso:** Basado en roles

### Estructura Modular
```
routes/
├── __init__.py         # Registro de blueprints
├── auth.py             # Autenticación
├── dashboard.py        # Panel principal y métricas
├── technical_service.py # Servicio técnico (ST)
├── internal_repair.py  # Reparación interna (RI)
├── warranty.py         # Garantías (GA)
├── view_technical.py   # Vistas técnicas
├── upload_images.py    # Carga de imágenes
└── onedrive.py         # Integración OneDrive
```

## 🚪 Módulos de Rutas

### 1. Dashboard (`dashboard.py`)

#### Propósito
Panel de control principal con métricas, KPIs y análisis de datos.

#### Endpoints Principales

##### `GET /dashboard`
```python
@dashboard_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def dashboard():
    """Página principal del dashboard"""
```
- **Propósito:** Renderiza la página principal del dashboard
- **Permisos:** Admin, posventa, jefeTienda
- **Retorna:** Template HTML con interfaz

##### `GET /dashboard/kpis`
```python
@dashboard_bp.route("/dashboard/kpis", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_kpis():
    """Obtiene KPIs del dashboard por período"""
```
- **Parámetros:**
  - `period`: today/week/month/year/all/custom
  - `start_date`: fecha inicio (para custom)
  - `end_date`: fecha fin (para custom)
- **Retorna:** JSON con métricas
- **Cache:** Redis con TTL de 5 minutos

##### `GET /dashboard/pending-tickets`
```python
@dashboard_bp.route("/dashboard/pending-tickets", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_pending_tickets():
    """Datos para tabla de tickets pendientes (PAGINADO)"""
```
- **Parámetros:**
  - `page`: número de página (default: 1)
  - `per_page`: elementos por página (default: 10)
- **Retorna:** JSON paginado con tickets

##### `GET /dashboard/tickets-by-technician`
```python
@dashboard_bp.route("/dashboard/tickets-by-technician", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_tickets_by_technician():
    """Distribución de tickets por técnico"""
```

##### `GET /dashboard/top-problems`
```python
@dashboard_bp.route("/dashboard/top-problems", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_top_problems():
    """Top 5 problemas más comunes"""
```

##### `GET /dashboard/tickets-distribution`
```python
@dashboard_bp.route("/dashboard/tickets-distribution", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_tickets_distribution():
    """Distribución por tipo de servicio"""
```

##### `GET /dashboard/timeline`
```python
@dashboard_bp.route("/dashboard/timeline", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "jefeTienda")
def get_timeline_data():
    """Datos de línea temporal de tickets"""
```

### 2. Technical Service (`technical_service.py`)

#### Propósito
Gestión completa de tickets de servicio técnico.

#### Endpoints Principales

##### `GET /technical-service`
```python
@technical_service_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def technical_service():
    """Lista de tickets de servicio técnico"""
```

##### `POST /technical-service/create`
```python
@technical_service_bp.route("/create", methods=["POST"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def create_ticket():
    """Crear nuevo ticket de servicio técnico"""
```
- **Datos requeridos:**
  - Información del cliente
  - Datos del producto
  - Problemas detectados
  - Técnico asignado

##### `GET /technical-service/edit/<int:ticket_id>`
```python
@technical_service_bp.route("/edit/<int:ticket_id>", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def edit_ticket_form(ticket_id):
    """Formulario de edición de ticket"""
```

##### `POST /technical-service/update/<int:ticket_id>`
```python
@technical_service_bp.route("/update/<int:ticket_id>", methods=["POST"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def update_ticket(ticket_id):
    """Actualizar ticket existente"""
```

##### `GET /technical-service/detail/<int:ticket_id>`
```python
@technical_service_bp.route("/detail/<int:ticket_id>", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def view_detail_ticket(ticket_id):
    """Ver detalles completos del ticket"""
```

### 3. Internal Repair (`internal_repair.py`)

#### Propósito
Gestión de tickets de reparación interna.

#### Endpoints Principales

##### `GET /internal-repair`
```python
@internal_repair_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin", "posventa")
def internal_repair():
    """Lista de tickets de reparación interna"""
```

##### `POST /internal-repair/create`
```python
@internal_repair_bp.route("/create", methods=["POST"])
@login_required
@role_required("Admin", "posventa")
def create_ticket():
    """Crear ticket de reparación interna"""
```

##### `GET /internal-repair/paginated`
```python
@internal_repair_bp.route("/paginated", methods=["GET"])
@login_required
@role_required("Admin", "posventa")
def get_paginated_tickets():
    """Obtener tickets paginados con filtros"""
```

### 4. Warranty (`warranty.py`)

#### Propósito
Gestión de garantías y procesos de devolución.

#### Endpoints Principales

##### `GET /warranty`
```python
@warranty_bp.route("/", methods=["GET"])
@login_required
@role_required("Admin", "posventa")
def warranty():
    """Lista de garantías"""
```

##### `POST /warranty/create`
```python
@warranty_bp.route("/create", methods=["POST"])
@login_required
@role_required("Admin", "posventa")
def create_warranty():
    """Crear nueva garantía"""
```

##### `GET /warranty/detail/<int:ticket_id>`
```python
@warranty_bp.route("/detail/<int:ticket_id>", methods=["GET"])
@login_required
@role_required("Admin", "posventa")
def view_detail_warranty(ticket_id):
    """Ver detalles de garantía"""
```

### 5. View Technical (`view_technical.py`)

#### Propósito
Vistas específicas para técnicos en campo.

#### Endpoints Principales

##### `GET /view-technical`
```python
@view_technical_bp.route("/", methods=["GET"])
@login_required
@role_required("servicioTecnico", "Admin")
def view_technical():
    """Vista principal para técnicos"""
```

##### `GET /view-technical/tickets/<document>`
```python
@view_technical_bp.route("/tickets/<document>", methods=["GET"])
@login_required
@role_required("servicioTecnico", "Admin")
def get_tickets_by_technician(document):
    """Tickets asignados a un técnico específico"""
```

### 6. Upload Images (`upload_images.py`)

#### Propósito
Manejo de carga y gestión de imágenes.

#### Endpoints Principales

##### `POST /upload`
```python
@upload_images_bp.route("/upload", methods=["POST"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def upload_file():
    """Subir archivo de imagen"""
```
- **Formatos soportados:** JPG, JPEG, PNG, GIF, WEBP
- **Tamaño máximo:** 16MB
- **Validaciones:** Tipo MIME, extensión, tamaño

### 7. OneDrive (`onedrive.py`)

#### Propósito
Integración con Microsoft OneDrive para almacenamiento.

#### Endpoints Principales

##### `POST /onedrive/upload`
```python
@onedrive_bp.route("/upload", methods=["POST"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def upload_to_onedrive():
    """Subir archivo a OneDrive"""
```

##### `GET /onedrive/files/<ticket_id>`
```python
@onedrive_bp.route("/files/<int:ticket_id>", methods=["GET"])
@login_required
@role_required("Admin", "posventa", "servicioTecnico")
def get_ticket_files(ticket_id):
    """Obtener archivos de un ticket"""
```

### 8. Authentication (`auth.py`)

#### Propósito
Gestión de autenticación y sesiones.

#### Endpoints Principales

##### `POST /login`
```python
@auth_bp.route("/login", methods=["POST"])
def login():
    """Autenticación de usuario"""
```

##### `GET /logout`
```python
@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Cerrar sesión"""
```

## 🛡️ Seguridad y Control de Acceso

### Decoradores de Seguridad

#### `@login_required`
```python
from flask_login import login_required

@login_required
def protected_endpoint():
    """Requiere autenticación"""
```

#### `@role_required(*roles)`
```python
from apps.tickets.utils.access_control import role_required

@role_required("Admin", "posventa")
def admin_endpoint():
    """Requiere roles específicos"""
```

### Roles del Sistema
- **Admin:** Acceso completo a todas las funciones
- **posventa:** Gestión de tickets y reportes
- **jefeTienda:** Visualización de métricas y supervisión
- **servicioTecnico:** Operación de tickets asignados

## 🔄 Manejo de Errores

### Códigos de Estado
- **200:** Operación exitosa
- **400:** Error de validación
- **401:** No autenticado
- **403:** Sin permisos
- **404:** Recurso no encontrado
- **500:** Error interno del servidor

### Estructura de Respuesta
```json
{
    "success": true/false,
    "data": {...},
    "message": {
        "title": "Título del mensaje",
        "text": "Descripción detallada",
        "icon": "success/error/warning/info"
    },
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 100,
        "pages": 10
    }
}
```

## 📊 Optimizaciones

### Cache Strategy
```python
from apps.tickets.services.cache_manager import cache_manager

@cache_manager.cached(timeout=300, key_prefix='dashboard_kpis')
def get_cached_kpis():
    """Datos cacheados por 5 minutos"""
```

### Paginación
```python
def get_paginated_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return {
        'data': pagination.items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
```

## 🔍 Filtros y Búsquedas

### Filtros Implementados
- **Por estado:** Sin asignar, Asignado, En proceso, etc.
- **Por técnico:** Documento del técnico
- **Por cliente:** Documento del cliente
- **Por fecha:** Rango de fechas
- **Por ciudad:** Ciudad de servicio
- **Por tipo:** ST, RI, GA

### Búsqueda de Texto
```python
def search_tickets(query):
    return Tickets.query.filter(
        or_(
            Tickets.document_client.like(f'%{query}%'),
            Tickets.reference.like(f'%{query}%'),
            Tickets.IMEI.like(f'%{query}%')
        )
    ).all()
```

## 📈 Métricas y Logging

### Logging por Endpoint
```python
import logging

logger = logging.getLogger(__name__)

@route('/example')
def example_endpoint():
    logger.info(f"Acceso a endpoint por usuario: {current_user.id}")
    try:
        # Lógica del endpoint
        logger.info("Operación exitosa")
    except Exception as e:
        logger.error(f"Error en endpoint: {str(e)}", exc_info=True)
```

### Métricas de Performance
- Tiempo de respuesta por endpoint
- Cantidad de requests por minuto
- Errores por tipo
- Uso de cache

## 🔧 Mantenimiento

### Endpoints de Administración
```python
@admin_required
def maintenance_endpoint():
    """Funciones de mantenimiento"""
```

### Health Checks
```python
@route('/health')
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

> ⚠️ **Nota importante sobre endpoints:**
> Al usar `url_for` en plantillas, asegúrate de emplear el nombre del blueprint registrado, por ejemplo:
> - Correcto: `url_for('internal_repair.create_ticketsRI')`
> - Incorrecto: `url_for('tickets.internal_repair.create_ticketsRI')`

(Reemplazar en todos los ejemplos de endpoints el prefijo 'tickets.' por el nombre real del blueprint, como 'warranty', 'internal_repair', etc.)

---

*Documentación del módulo Routes - Sistema de Tickets* 