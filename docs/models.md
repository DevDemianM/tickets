# Documentación - Módulo Models

## 📋 Información General

**Módulo:** `apps.tickets.models`  
**Propósito:** Definición de modelos de datos y estructura de base de datos  
**Ubicación:** `apps/tickets/models/`  

## 🏗️ Arquitectura de Datos

### Base de Datos
- **Motor:** SQL Server
- **Esquema:** `plan_beneficios`
- **Binding:** `db4`
- **ORM:** SQLAlchemy

### Patrones Implementados
- **Model Relationships**
- **Timezone Management**
- **Data Validation**

## 📊 Modelos Principales

### 1. Tickets (`tickets.py`)

#### Descripción
Modelo principal que representa un ticket de servicio técnico, reparación interna o garantía.

#### Estructura de Datos
```python
class Tickets(db.Model, UserMixin):
    __bind_key__ = "db4"
    __tablename__ = "Tickets"
    __table_args__ = {"schema": "plan_beneficios"}
```

#### Campos Principales
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `id_ticket` | Integer | ID único del ticket | ✅ |
| `state` | String(50) | Estado actual del ticket | ✅ |
| `priority` | String(50) | Prioridad (Alta/Media/Baja) | ✅ |
| `technical_name` | String(33) | Nombre del técnico asignado | ✅ |
| `technical_document` | String(11) | Documento del técnico | ✅ |
| `document_client` | String(11) | Documento del cliente | ✅ |
| `product_code` | String(50) | Código del producto | ✅ |
| `IMEI` | String(20) | IMEI del dispositivo | ✅ |
| `reference` | String(100) | Referencia del producto | ✅ |
| `type_of_service` | String(100) | Tipo de servicio (0:ST, 1:RI, 2:GA) | ✅ |
| `city` | String(15) | Ciudad del servicio | ✅ |

#### Campos de Tiempo
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `creation_date` | DateTime | Fecha de creación |
| `assigned` | DateTime | Fecha de asignación |
| `in_progress` | DateTime | Fecha de inicio |
| `in_revision` | DateTime | Fecha de revisión |
| `finished` | DateTime | Fecha de finalización |

#### Campos Financieros
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `spare_value` | Numeric(12,2) | Valor de repuestos |
| `service_value` | Numeric(12,2) | Valor del servicio |
| `discounted_value` | Numeric(12,2) | Valor descontado |
| `total` | Numeric(12,2) | Total facturado |

#### Métodos Principales

##### `get_colombia_utc_now()`
```python
def get_colombia_utc_now():
    """
    FUNCIÓN HELPER: Obtiene la hora actual de Colombia y la convierte a UTC
    para guardar consistentemente en la base de datos
    """
    zona_bogota = pytz.timezone('America/Bogota')
    hora_colombia = datetime.now(tz=zona_bogota)
    return hora_colombia.astimezone(pytz.UTC).replace(tzinfo=None)
```

##### `update_state(new_state)`
```python
def update_state(self, new_state):
    """Actualiza el estado del ticket y registra la hora del cambio"""
    self.state = new_state
    now = get_colombia_utc_now()
    
    if new_state == "Asignado":
        self.assigned = now
    elif new_state == "En proceso":
        self.in_progress = now
    elif new_state == "En Revision":
        self.in_revision = now
    elif new_state == "Terminado":
        self.finished = now
    
    return now
```

##### `get_spare_parts()`
```python
def get_spare_parts(self):
    """Obtiene los repuestos asociados al ticket"""
    spare_tickets = Spares_tickets.query.filter_by(
        id_ticket=self.id_ticket).all()
    return spare_tickets
```

#### Relaciones
```python
# Relación many-to-many con Problems
problems = db.relationship("Problems",
                         secondary=Problems_tickets.__table__,
                         backref=db.backref("tickets", lazy="dynamic"),
                         lazy="dynamic")
```

### 2. Employees (`employees.py`)

#### Descripción
Modelo que representa los empleados del sistema.

#### Estructura
```python
class Employees(db.Model):
    __bind_key__ = "db4"
    __tablename__ = "Employees"
    __table_args__ = {"schema": "plan_beneficios"}
```

#### Campos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único |
| `document` | String(11) | Documento de identidad |
| `name` | String(33) | Nombre completo |
| `role` | String(50) | Rol en el sistema |
| `city` | String(15) | Ciudad de trabajo |

### 3. Problems (`problems.py`)

#### Descripción
Catálogo de problemas técnicos que pueden presentar los equipos.

#### Estructura
```python
class Problems(db.Model):
    __bind_key__ = "db4"
    __tablename__ = "Problems"
    __table_args__ = {"schema": "plan_beneficios"}
```

#### Campos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único |
| `name` | String(250) | Descripción del problema |

### 4. Spares (`spares.py`)

#### Descripción
Catálogo de repuestos disponibles.

#### Estructura
```python
class Spares(db.Model):
    __bind_key__ = "db4"
    __tablename__ = "Spares"
    __table_args__ = {"schema": "plan_beneficios"}
```

#### Campos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único |
| `name` | String(250) | Nombre del repuesto |

### 5. Problems_tickets (`problemsTickets.py`)

#### Descripción
Tabla de unión many-to-many entre tickets y problemas.

#### Estructura
```python
Problems_tickets = db.Table('Problems_tickets',
    db.Column('id_problems', db.Integer, 
              db.ForeignKey('plan_beneficios.Problems.id'), 
              primary_key=True),
    db.Column('id_ticket', db.Integer, 
              db.ForeignKey('plan_beneficios.Tickets.id_ticket'), 
              primary_key=True),
    schema="plan_beneficios"
)
```

### 6. Spares_tickets (`sparesTickets.py`)

#### Descripción
Tabla de unión entre tickets y repuestos con información adicional.

#### Estructura
```python
class Spares_tickets(db.Model):
    __bind_key__ = "db4"
    __tablename__ = "Spares_tickets"
    __table_args__ = {"schema": "plan_beneficios"}
```

#### Campos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_spares` | Integer | ID del repuesto |
| `id_ticket` | Integer | ID del ticket |
| `quantity` | Integer | Cantidad utilizada |
| `price` | Numeric(12,2) | Precio unitario |

## 🔄 Estados del Sistema

### Estados de Tickets
1. **Sin asignar** - Ticket creado, pendiente de asignación
2. **Asignado** - Asignado a técnico, pendiente de inicio
3. **En proceso** - En diagnóstico o reparación
4. **En Revision** - Pendiente de aprobación
5. **Terminado** - Completado y entregado

### Tipos de Servicio
- **0:** Servicio Técnico (ST)
- **1:** Reparación Interna (RI)
- **2:** Garantía (GA)

### Niveles de Prioridad
- **Alta:** Casos urgentes o críticos
- **Media:** Casos normales
- **Baja:** Casos de menor urgencia

## 🕐 Manejo de Zonas Horarias

### Implementación
```python
import pytz
from datetime import datetime

def get_colombia_utc_now():
    """Obtiene la hora de Colombia convertida a UTC"""
    zona_bogota = pytz.timezone('America/Bogota')
    hora_colombia = datetime.now(tz=zona_bogota)
    return hora_colombia.astimezone(pytz.UTC).replace(tzinfo=None)
```

### Uso
- Todas las fechas se almacenan en UTC
- Las conversiones se realizan en el frontend
- La zona horaria de referencia es `America/Bogota`


### Consultas Comunes
```python
# Obtener tickets con problemas
ticket = Tickets.query.get(id)
problems = ticket.problems.all()

# Obtener repuestos de un ticket
spare_parts = ticket.get_spare_parts()

# Tickets por técnico
tickets = Tickets.query.filter_by(
    technical_document=document
).all()
```

## 🛡️ Validaciones

### Validaciones de Modelo
- Campos requeridos validados en el modelo
- Longitudes máximas definidas
- Tipos de datos estrictos

### Validaciones de Negocio
- Estados válidos del sistema
- Transiciones de estado permitidas
- Valores numéricos positivos

## 📈 Optimizaciones

### Índices Recomendados
```sql
-- Índices principales
CREATE INDEX IX_Tickets_State ON plan_beneficios.Tickets(state);
CREATE INDEX IX_Tickets_Technical ON plan_beneficios.Tickets(technical_document);
CREATE INDEX IX_Tickets_Client ON plan_beneficios.Tickets(document_client);
CREATE INDEX IX_Tickets_Creation ON plan_beneficios.Tickets(creation_date);
CREATE INDEX IX_Tickets_Type ON plan_beneficios.Tickets(type_of_service);
```

### Consultas Optimizadas
- Uso de eager loading para relaciones
- Filtros en consultas SQL nativas
- Paginación para grandes datasets

## 🔧 Mantenimiento

### Tareas Regulares
- Limpieza de tickets antiguos
- Actualización de índices
- Validación de integridad referencial

### Monitoreo
- Performance de consultas
- Crecimiento de tablas
- Integridad de datos

---

*Documentación del módulo Models - Sistema de Tickets* 