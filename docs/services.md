# Documentación - Módulo Services

## 📋 Información General

**Módulo:** `apps.tickets.services`  
**Propósito:** Lógica de negocio y servicios especializados  
**Ubicación:** `apps/tickets/services/`  

## 🏗️ Arquitectura de Servicios

### Service Layer Pattern
- **Separación de responsabilidades**
- **Reutilización de código**
- **Testabilidad mejorada**
- **Mantenimiento simplificado**

### Estructura Modular
```
services/
├── cache_manager.py              # Gestión de cache
├── connection_manager.py         # Pool de conexiones
├── pagination_service.py         # Servicios de paginación
├── queries.py                   # Consultas optimizadas
├── ticket_email_service.py      # Notificaciones por email
├── optimized_technical_service.py    # ST optimizado
├── optimized_internal_repair_service.py # RI optimizado
└── optimized_warranty_service.py     # GA optimizado
```

## 🚀 Servicios Principales

### 1. Cache Manager (`cache_manager.py`)

#### Propósito
Gestión inteligente de cache para optimizar rendimiento del sistema.

#### Configuración
```python
class CacheManager:
    def __init__(self, app=None, config_prefix='CACHE'):
        self.app = app
        self.config_prefix = config_prefix
        self._cache = None
```

#### Métodos Principales

##### `cached(timeout, key_prefix)`
```python
def cached(self, timeout=300, key_prefix='view'):
    """Decorador para cache automático"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = self._generate_cache_key(
                key_prefix, f.__name__, args, kwargs
            )
            
            # Intentar obtener del cache
            result = self._cache.get(cache_key)
            if result is not None:
                return result
            
            # Ejecutar función y cachear resultado
            result = f(*args, **kwargs)
            self._cache.set(cache_key, result, timeout=timeout)
            return result
        return decorated_function
    return decorator
```

##### `invalidate_pattern(pattern)`
```python
def invalidate_pattern(self, pattern):
    """Invalida cache por patrón"""
    keys = self._cache.keys(f"{pattern}*")
    if keys:
        self._cache.delete_many(keys)
```

#### Estrategias de Cache
- **Dashboard KPIs:** 5 minutos
- **Tickets paginados:** 2 minutos
- **Catálogos:** 30 minutos
- **Métricas complejas:** 10 minutos

### 2. Connection Manager (`connection_manager.py`)

#### Propósito
Gestión eficiente del pool de conexiones a la base de datos.

#### Configuración
```python
class ConnectionManager:
    def __init__(self):
        self.pool_size = 20
        self.max_overflow = 30
        self.pool_timeout = 30
        self.pool_recycle = 3600
```

#### Métodos Principales

##### `get_connection()`
```python
def get_connection(self):
    """Obtiene conexión del pool"""
    try:
        connection = self.engine.connect()
        return connection
    except Exception as e:
        logger.error(f"Error obteniendo conexión: {e}")
        raise
```

##### `execute_query(query, params=None)`
```python
def execute_query(self, query, params=None):
    """Ejecuta consulta con manejo de conexiones"""
    with self.get_connection() as conn:
        try:
            result = conn.execute(text(query), params or {})
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            raise
```

### 3. Pagination Service (`pagination_service.py`)

#### Propósito
Servicio especializado para paginación eficiente de grandes datasets.

#### Métodos Principales

##### `paginate_query(query, page, per_page)`
```python
def paginate_query(self, query, page=1, per_page=10):
    """Pagina consulta SQLAlchemy"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': math.ceil(total / per_page),
        'has_next': page * per_page < total,
        'has_prev': page > 1
    }
```

##### `paginate_raw_query(query, params, page, per_page)`
```python
def paginate_raw_query(self, query, params, page=1, per_page=10):
    """Pagina consulta SQL nativa"""
    # Consulta de conteo
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
    total = self.connection_manager.execute_query(count_query, params)[0]['total']
    
    # Consulta paginada
    offset = (page - 1) * per_page
    paginated_query = f"{query} OFFSET {offset} ROWS FETCH NEXT {per_page} ROWS ONLY"
    items = self.connection_manager.execute_query(paginated_query, params)
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': math.ceil(total / per_page)
    }
```

### 4. Queries (`queries.py`)

#### Propósito
Repositorio de consultas SQL optimizadas para el sistema.

#### Consultas Principales

##### Dashboard KPIs
```sql
-- Tickets activos por estado
SELECT 
    state,
    COUNT(*) as count
FROM plan_beneficios.Tickets 
WHERE creation_date >= %s AND creation_date <= %s
GROUP BY state
```

##### Métricas Temporales
```sql
-- Tendencia temporal de tickets
SELECT 
    CAST(creation_date AS DATE) as date,
    type_of_service,
    COUNT(*) as count
FROM plan_beneficios.Tickets
WHERE creation_date >= %s AND creation_date <= %s
GROUP BY CAST(creation_date AS DATE), type_of_service
ORDER BY date
```

##### Top Problemas
```sql
-- Problemas más comunes
SELECT 
    p.name,
    COUNT(pt.id_ticket) as frequency
FROM plan_beneficios.Problems p
INNER JOIN plan_beneficios.Problems_tickets pt ON p.id = pt.id_problems
INNER JOIN plan_beneficios.Tickets t ON pt.id_ticket = t.id_ticket
WHERE t.creation_date >= %s AND t.creation_date <= %s
GROUP BY p.id, p.name
ORDER BY frequency DESC
LIMIT 5
```

### 5. Ticket Email Service (`ticket_email_service.py`)

#### Propósito
Servicio de notificaciones por email para eventos del sistema.

#### Configuración
```python
class TicketEmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
```

#### Métodos Principales

##### `send_ticket_notification(ticket, event_type)`
```python
def send_ticket_notification(self, ticket, event_type):
    """Envía notificación de ticket"""
    template_map = {
        'created': 'ticket_created.html',
        'assigned': 'ticket_assigned.html',
        'completed': 'ticket_completed.html',
        'cancelled': 'ticket_cancelled.html'
    }
    
    template = template_map.get(event_type)
    if not template:
        return False
    
    # Preparar datos del email
    email_data = self._prepare_email_data(ticket, event_type)
    
    # Enviar email
    return self._send_email(
        to=email_data['recipient'],
        subject=email_data['subject'],
        template=template,
        data=email_data
    )
```

##### `send_daily_report()`
```python
def send_daily_report(self):
    """Envía reporte diario a supervisores"""
    # Recopilar métricas del día
    report_data = self._generate_daily_metrics()
    
    # Enviar a lista de supervisores
    supervisors = self._get_supervisor_emails()
    
    for supervisor in supervisors:
        self._send_email(
            to=supervisor,
            subject=f"Reporte Diario - {datetime.now().strftime('%Y-%m-%d')}",
            template='daily_report.html',
            data=report_data
        )
```

### 6. Optimized Technical Service (`optimized_technical_service.py`)

#### Propósito
Servicios optimizados para gestión de tickets de servicio técnico.

#### Métodos Principales

##### `get_tickets_paginated(filters, page, per_page)`
```python
def get_tickets_paginated(self, filters=None, page=1, per_page=10):
    """Obtiene tickets ST con paginación optimizada"""
    
    # Construir consulta base
    base_query = """
    SELECT t.*, e.name as technician_name
    FROM plan_beneficios.Tickets t
    LEFT JOIN plan_beneficios.Employees e ON t.technical_document = e.document
    WHERE t.type_of_service = '0'
    """
    
    # Aplicar filtros
    if filters:
        base_query += self._build_filter_clause(filters)
    
    # Ordenar por prioridad y fecha
    base_query += """
    ORDER BY 
        CASE t.priority 
            WHEN 'Alta' THEN 1 
            WHEN 'Media' THEN 2 
            WHEN 'Baja' THEN 3 
            ELSE 4 
        END,
        t.creation_date ASC
    """
    
    # Paginar resultados
    return self.pagination_service.paginate_raw_query(
        base_query, filters or {}, page, per_page
    )
```

##### `create_ticket(ticket_data)`
```python
def create_ticket(self, ticket_data):
    """Crea ticket ST con validaciones y notificaciones"""
    
    # Validar datos
    validation_result = self._validate_ticket_data(ticket_data)
    if not validation_result['valid']:
        return validation_result
    
    # Crear ticket
    ticket = Tickets(**ticket_data)
    ticket.type_of_service = '0'  # Servicio Técnico
    ticket.creation_date = get_colombia_utc_now()
    
    db.session.add(ticket)
    db.session.commit()
    
    # Invalidar cache relacionado
    self.cache_manager.invalidate_pattern('dashboard_*')
    self.cache_manager.invalidate_pattern('technical_service_*')
    
    # Enviar notificación
    self.email_service.send_ticket_notification(ticket, 'created')
    
    return {'success': True, 'ticket': ticket}
```

### 7. Optimized Internal Repair Service (`optimized_internal_repair_service.py`)

#### Propósito
Servicios especializados para reparaciones internas.

#### Métodos Principales

##### `get_repair_metrics(period)`
```python
def get_repair_metrics(self, period='month'):
    """Obtiene métricas de reparaciones internas"""
    
    cache_key = f"ri_metrics_{period}"
    cached_result = self.cache_manager.get(cache_key)
    
    if cached_result:
        return cached_result
    
    # Consulta optimizada para métricas
    query = """
    SELECT 
        COUNT(*) as total_repairs,
        AVG(DATEDIFF(day, creation_date, finished)) as avg_repair_time,
        SUM(total) as total_revenue,
        COUNT(CASE WHEN state = 'Terminado' THEN 1 END) as completed_repairs
    FROM plan_beneficios.Tickets
    WHERE type_of_service = '1'
    AND creation_date >= %s
    """
    
    date_range = self._get_date_range(period)
    result = self.connection_manager.execute_query(query, [date_range['start']])
    
    # Cachear por 10 minutos
    self.cache_manager.set(cache_key, result[0], timeout=600)
    
    return result[0]
```

### 8. Optimized Warranty Service (`optimized_warranty_service.py`)

#### Propósito
Servicios especializados para gestión de garantías.

#### Métodos Principales

##### `process_warranty_claim(warranty_data)`
```python
def process_warranty_claim(self, warranty_data):
    """Procesa reclamo de garantía"""
    
    # Validar elegibilidad de garantía
    eligibility = self._check_warranty_eligibility(warranty_data)
    if not eligibility['eligible']:
        return eligibility
    
    # Crear ticket de garantía
    warranty_ticket = Tickets(**warranty_data)
    warranty_ticket.type_of_service = '2'  # Garantía
    warranty_ticket.state = 'En Revision'  # Requiere aprobación
    
    db.session.add(warranty_ticket)
    db.session.commit()
    
    # Notificar a supervisores
    self.email_service.send_warranty_notification(warranty_ticket)
    
    return {'success': True, 'warranty': warranty_ticket}
```

## 🔄 Patrones de Diseño Implementados

### 1. Repository Pattern
```python
class TicketRepository:
    def find_by_id(self, ticket_id):
        return Tickets.query.get(ticket_id)
    
    def find_by_criteria(self, criteria):
        query = Tickets.query
        for key, value in criteria.items():
            query = query.filter(getattr(Tickets, key) == value)
        return query.all()
```

### 2. Factory Pattern
```python
class ServiceFactory:
    @staticmethod
    def create_service(service_type):
        services = {
            'technical': OptimizedTechnicalService,
            'repair': OptimizedInternalRepairService,
            'warranty': OptimizedWarrantyService
        }
        return services[service_type]()
```

### 3. Observer Pattern
```python
class TicketEventObserver:
    def on_ticket_created(self, ticket):
        # Enviar notificaciones
        # Actualizar métricas
        # Invalidar cache
        pass
```

## 📊 Optimizaciones de Performance

### Consultas Optimizadas
- Uso de índices apropiados
- Consultas SQL nativas para casos complejos
- Lazy loading para relaciones
- Aggregate queries para métricas

### Cache Strategy
```python
# Cache de diferentes niveles
@cache_manager.cached(timeout=300, key_prefix='dashboard')
def get_dashboard_kpis():
    # KPIs del dashboard - 5 minutos

@cache_manager.cached(timeout=1800, key_prefix='catalog')
def get_problems_catalog():
    # Catálogos - 30 minutos

@cache_manager.cached(timeout=120, key_prefix='tickets')
def get_tickets_paginated():
    # Listados paginados - 2 minutos
```

### Connection Pooling
```python
# Configuración de pool optimizada
engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

## 🛡️ Validaciones y Seguridad

### Validación de Datos
```python
def validate_ticket_data(self, data):
    """Valida datos de ticket"""
    errors = []
    
    # Validaciones requeridas
    required_fields = ['document_client', 'product_code', 'IMEI']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} es requerido')
    
    # Validaciones de formato
    if data.get('document_client') and not re.match(r'^\d{7,11}$', data['document_client']):
        errors.append('Documento de cliente inválido')
    
    return {'valid': len(errors) == 0, 'errors': errors}
```

### Sanitización
```python
def sanitize_input(self, data):
    """Sanitiza datos de entrada"""
    if isinstance(data, str):
        # Remover caracteres peligrosos
        data = re.sub(r'[<>\"\'%;()&+]', '', data)
        data = data.strip()
    
    return data
```

## 📈 Monitoreo y Métricas

### Performance Monitoring
```python
class PerformanceMonitor:
    def measure_execution_time(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log métricas
            logger.info(f"{func.__name__} ejecutado en {execution_time:.3f}s")
            
            return result
        return wrapper
```

### Health Checks
```python
def check_service_health(self):
    """Verifica salud de servicios"""
    health_status = {
        'database': self._check_database_connection(),
        'cache': self._check_cache_connection(),
        'email': self._check_email_service()
    }
    
    return {
        'healthy': all(health_status.values()),
        'services': health_status
    }
```

## 🔧 Mantenimiento

### Tareas de Limpieza
```python
def cleanup_old_cache_entries(self):
    """Limpia entradas de cache expiradas"""
    expired_keys = self.cache_manager.get_expired_keys()
    self.cache_manager.delete_many(expired_keys)

def archive_old_tickets(self, days=365):
    """Archiva tickets antiguos"""
    cutoff_date = datetime.now() - timedelta(days=days)
    old_tickets = Tickets.query.filter(
        Tickets.creation_date < cutoff_date,
        Tickets.state == 'Terminado'
    ).all()
    
    # Mover a tabla de archivo
    for ticket in old_tickets:
        self._archive_ticket(ticket)
```

---

*Documentación del módulo Services - Sistema de Tickets v2.1.0* 