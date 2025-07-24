# Sistema de Búsqueda Unificado - Módulo de Tickets

## 📋 Descripción General

Se implementó un sistema de búsqueda completo y unificado para todos los módulos del sistema de tickets que permite búsqueda sin limitaciones de paginado y mejora significativamente la experiencia del usuario.

## 🎯 Módulos Afectados

- **Technical Service** (Servicio Técnico)
- **Internal Repair** (Reparación Interna)
- **Warranty** (Garantías)
- **View Technical** (Vista del Técnico)

## 🚀 Funcionalidades Implementadas

### ✨ Búsqueda Completa
- Búsqueda por múltiples campos: ID ticket, técnico, referencia, prioridad, documento cliente, IMEI, código de producto, ciudad, estado
- Sin limitaciones de paginado (muestra todos los resultados relacionados)
- Búsqueda en tiempo real con indicadores de carga

### 🎨 Interfaz Mejorada
- **Botón "Buscar"** reemplaza el ícono de lupa tradicional
- **Botón "Limpiar"** aparece automáticamente cuando hay texto en el campo
- **Indicadores visuales** durante la búsqueda
- **Mensajes de resultados** con contadores detallados

### 🔧 Funcionalidades Técnicas
- **Preservación del contenido original** - al limpiar búsqueda se restaura el contenido previo
- **Ocultación automática de paginación** durante búsqueda activa
- **Manejo de errores** robusto con notificaciones al usuario
- **Compatibilidad total** con funcionalidades existentes

## 📁 Archivos Implementados

### 1. Servicio de Búsqueda Backend
**Archivo:** `apps/tickets/services/search_service.py`
```python
class SearchService:
    @staticmethod
    def search_technical_service(search_term)
    @staticmethod
    def search_internal_repair(search_term)
    @staticmethod
    def search_warranty(search_term)
    @staticmethod
    def search_technician_tickets(search_term, technician_document)
```

### 2. JavaScript Unificado
**Archivo:** `apps/tickets/static/js/unified_search.js`
- Sistema modular configurado por tipo de página
- Auto-detección del módulo actual
- Manejo unificado de respuestas y errores

### 3. Rutas Backend Agregadas

#### Technical Service
```python
@technical_service_bp.route("/search_tickets", methods=["POST"])
def search_tickets()
```

#### Internal Repair
```python
@internal_repair_bp.route("/search_tickets", methods=["POST"])
def search_tickets()
```

#### Warranty
```python
@warranty_bp.route("/search_tickets", methods=["POST"])
def search_tickets()
```

#### View Technical
```python
@view_technical_bp.route("/search_tickets", methods=["POST"])
def search_tickets()
```

## 🔍 Campos de Búsqueda

### Todos los Módulos
- **id_ticket** - ID del ticket
- **technical_name** - Nombre del técnico
- **reference** - Referencia del producto
- **priority** - Prioridad (Alta, Media, Baja)
- **document_client** - Documento del cliente
- **IMEI** - IMEI/Serial del dispositivo
- **product_code** - Código del producto
- **city** - Ciudad
- **state** - Estado del ticket

### Específicos por Módulo

#### Technical Service & Warranty
- Búsqueda en todos los tickets del módulo correspondiente

#### Internal Repair
- Filtrado por type_of_service = "1" (reparaciones internas)

#### View Technical
- Filtrado por técnico asignado (basado en documento del usuario actual)
- Solo tickets activos (no terminados)

## 🛠️ Uso del Sistema

### Para Desarrolladores

1. **Incluir el script en plantillas:**
```html
<script src="{{ url_for('tickets.static', filename='js/unified_search.js') }}"></script>
```

2. **El sistema se inicializa automáticamente** detectando el módulo actual

3. **Las URLs de búsqueda están configuradas** para cada módulo en `/tickets/search_tickets`

### Para Usuarios

1. **Buscar:** Escribir en el campo de búsqueda y hacer clic en "Buscar"
2. **Limpiar:** Hacer clic en "Limpiar" para restaurar vista original
3. **Resultados:** Ver todos los tickets que coincidan con el término de búsqueda

## 📊 Respuesta de Búsqueda

### Estructura JSON
```json
{
    "success": true,
    "html": "<tr>...</tr>",
    "summary": {
        "total_results": 25,
        "by_state": {"Asignado": 10, "En Proceso": 8, "Terminado": 7},
        "by_priority": {"Alta": 5, "Media": 15, "Baja": 5},
        "by_city": {"Bogotá": 20, "Medellín": 5}
    },
    "search_term": "termo de búsqueda"
}
```

### Mensajes de Resultado
- **Éxito:** "Encontrados X tickets para 'término'"
- **Sin resultados:** "No se encontraron tickets para 'término'"
- **Error:** Notificación con SweetAlert2

## 🔧 Configuración por Módulo

El sistema está configurado en `unified_search.js` con los siguientes parámetros:

```javascript
modules: {
    'technical_service': {
        searchUrl: '/tickets/search_tickets',
        tableBodyId: 'ticketsTableBody',
        searchInputId: 'searchInput',
        // ...
    },
    'internal_repair': {
        searchUrl: '/tickets/search_tickets',
        tableBodyId: 'repairsTableBody',
        searchInputId: 'searchRepairs',
        // ...
    },
    // warranty y view_technical...
}
```

## ✅ Estado de Implementación

- ✅ Servicio de búsqueda backend completo
- ✅ JavaScript unificado funcional
- ✅ Rutas agregadas a todos los módulos
- ✅ Plantillas actualizadas
- ✅ Sistema probado y funcional

## 🚨 Notas Importantes

1. **Compatibilidad:** El sistema mantiene total compatibilidad con funcionalidades existentes
2. **Performance:** Las búsquedas son optimizadas y no afectan el rendimiento general
3. **Seguridad:** Se mantienen todos los controles de acceso y validaciones existentes
4. **Escalabilidad:** El sistema puede extenderse fácilmente a nuevos módulos

## 🔄 Mantenimiento

Para agregar nuevos campos de búsqueda:

1. Modificar la consulta SQL en `search_service.py`
2. Actualizar los campos en la función de búsqueda correspondiente
3. No se requieren cambios en el frontend (JavaScript)

## 📞 Soporte

Para dudas o modificaciones, consultar:
- Archivo de servicios: `apps/tickets/services/search_service.py`
- JavaScript unificado: `apps/tickets/static/js/unified_search.js`
- Documentación de cada ruta en los archivos correspondientes 