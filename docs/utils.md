# Documentación - Módulo Utils

## 📋 Información General

**Módulo:** `apps.tickets.utils`  
**Propósito:** Utilidades, helpers y funciones auxiliares  
**Ubicación:** `apps/tickets/utils/`  

## 🏗️ Arquitectura de Utilidades

### Principios de Diseño
- **Reutilización:** Funciones auxiliares compartidas
- **Separación de responsabilidades:** Cada utility tiene un propósito específico
- **Testabilidad:** Funciones puras cuando es posible
- **Rendimiento:** Optimizadas para uso frecuente

### Estructura Modular
```
utils/
├── __init__.py           # Importaciones y configuración
└── access_control.py     # Control de acceso y permisos
```

## 🛡️ Control de Acceso (`access_control.py`)

### Propósito
Gestión centralizada de permisos y control de acceso basado en roles.

### Características
- **Decoradores de autorización**
- **Validación de roles**
- **Control granular de permisos**
- **Logging de accesos**

### Implementación Principal

#### Decorador `role_required`
```python
from functools import wraps
from flask import session, redirect, url_for, flash, current_app
import logging

logger = logging.getLogger(__name__)

def role_required(*allowed_roles):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados
    
    Args:
        *allowed_roles: Roles permitidos para acceder al endpoint
        
    Returns:
        Decorador que valida permisos
        
    Example:
        @role_required("Admin", "posventa")
        def admin_endpoint():
            return "Acceso autorizado"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener roles del usuario desde la sesión
            user_roles = session.get('user_roles', [])
            
            # Log del intento de acceso
            user_id = session.get('user_id', 'Unknown')
            logger.info(f"Usuario {user_id} intentando acceder a {f.__name__} con roles: {user_roles}")
            
            # Verificar si el usuario tiene alguno de los roles requeridos
            if not any(role in user_roles for role in allowed_roles):
                logger.warning(f"Acceso denegado a {f.__name__} para usuario {user_id}")
                flash(
                    f'Acceso denegado. Se requiere uno de los siguientes roles: {", ".join(allowed_roles)}',
                    'danger'
                )
                return redirect(url_for('home'))
            
            # Log de acceso exitoso
            logger.info(f"Acceso autorizado a {f.__name__} para usuario {user_id}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

#### Función `check_permission`
```python
def check_permission(user_roles, required_roles):
    """
    Verifica si los roles del usuario incluyen alguno de los requeridos
    
    Args:
        user_roles (list): Roles del usuario actual
        required_roles (list): Roles requeridos para la acción
        
    Returns:
        bool: True si tiene permisos, False en caso contrario
    """
    if not user_roles or not required_roles:
        return False
    
    return any(role in user_roles for role in required_roles)
```

#### Función `get_user_permissions`
```python
def get_user_permissions(user_roles):
    """
    Obtiene la lista completa de permisos basada en los roles del usuario
    
    Args:
        user_roles (list): Roles del usuario
        
    Returns:
        dict: Diccionario con permisos organizados por módulo
    """
    permissions = {
        'dashboard': {
            'view': False,
            'export': False
        },
        'tickets': {
            'view': False,
            'create': False,
            'edit': False,
            'delete': False
        },
        'warranty': {
            'view': False,
            'create': False,
            'approve': False
        },
        'admin': {
            'manage_users': False,
            'view_logs': False,
            'system_config': False
        }
    }
    
    # Permisos por rol
    role_permissions = {
        'Admin': {
            'dashboard': ['view', 'export'],
            'tickets': ['view', 'create', 'edit', 'delete'],
            'warranty': ['view', 'create', 'approve'],
            'admin': ['manage_users', 'view_logs', 'system_config']
        },
        'posventa': {
            'dashboard': ['view', 'export'],
            'tickets': ['view', 'create', 'edit'],
            'warranty': ['view', 'create']
        },
        'jefeTienda': {
            'dashboard': ['view', 'export'],
            'tickets': ['view'],
            'warranty': ['view']
        },
        'servicioTecnico': {
            'tickets': ['view', 'edit']
        }
    }
    
    # Aplicar permisos basados en roles
    for role in user_roles:
        if role in role_permissions:
            for module, actions in role_permissions[role].items():
                for action in actions:
                    if module in permissions and action in permissions[module]:
                        permissions[module][action] = True
    
    return permissions
```

#### Función `validate_access_level`
```python
def validate_access_level(required_level, user_roles):
    """
    Valida el nivel de acceso requerido contra los roles del usuario
    
    Args:
        required_level (str): Nivel requerido (basic, intermediate, advanced, admin)
        user_roles (list): Roles del usuario
        
    Returns:
        bool: True si cumple el nivel de acceso
    """
    access_levels = {
        'basic': ['servicioTecnico', 'jefeTienda', 'posventa', 'Admin'],
        'intermediate': ['jefeTienda', 'posventa', 'Admin'],
        'advanced': ['posventa', 'Admin'],
        'admin': ['Admin']
    }
    
    allowed_roles = access_levels.get(required_level, [])
    return any(role in user_roles for role in allowed_roles)
```

### Decoradores Adicionales

#### `admin_required`
```python
def admin_required(f):
    """Decorador que requiere rol de administrador"""
    return role_required("Admin")(f)
```

#### `technical_access`
```python
def technical_access(f):
    """Decorador para acceso técnico (técnicos y supervisores)"""
    return role_required("servicioTecnico", "posventa", "Admin")(f)
```

#### `supervisor_access`
```python
def supervisor_access(f):
    """Decorador para acceso de supervisión"""
    return role_required("jefeTienda", "posventa", "Admin")(f)
```

## 🔧 Utilidades Generales

### Validación de Datos
```python
import re
from datetime import datetime

def validate_document(document):
    """
    Valida formato de documento de identidad colombiano
    
    Args:
        document (str): Documento a validar
        
    Returns:
        bool: True si es válido
    """
    if not document:
        return False
    
    # Remover espacios y caracteres no numéricos
    clean_doc = re.sub(r'[^\d]', '', str(document))
    
    # Validar longitud (7-11 dígitos)
    if len(clean_doc) < 7 or len(clean_doc) > 11:
        return False
    
    return True

def validate_imei(imei):
    """
    Valida formato de IMEI
    
    Args:
        imei (str): IMEI a validar
        
    Returns:
        bool: True si es válido
    """
    if not imei:
        return False
    
    # Limpiar IMEI
    clean_imei = re.sub(r'[^\d]', '', str(imei))
    
    # IMEI debe tener 15 dígitos
    if len(clean_imei) != 15:
        return False
    
    return True

def validate_email(email):
    """
    Valida formato de email
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True si es válido
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### Formateadores
```python
def format_currency(amount):
    """
    Formatea cantidad como moneda colombiana
    
    Args:
        amount (float): Cantidad a formatear
        
    Returns:
        str: Cantidad formateada
    """
    if amount is None:
        return "$0"
    
    try:
        # Formatear con separadores de miles
        formatted = "${:,.0f}".format(float(amount))
        # Reemplazar comas por puntos (formato colombiano)
        return formatted.replace(',', '.')
    except (ValueError, TypeError):
        return "$0"

def format_phone(phone):
    """
    Formatea número telefónico
    
    Args:
        phone (str): Teléfono a formatear
        
    Returns:
        str: Teléfono formateado
    """
    if not phone:
        return ""
    
    # Limpiar número
    clean_phone = re.sub(r'[^\d]', '', str(phone))
    
    # Formatear según longitud
    if len(clean_phone) == 7:
        # Número local: 123-4567
        return f"{clean_phone[:3]}-{clean_phone[3:]}"
    elif len(clean_phone) == 10:
        # Celular: (301) 234-5678
        return f"({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
    else:
        return clean_phone

def format_date(date_obj, format_type='short'):
    """
    Formatea fecha según el tipo especificado
    
    Args:
        date_obj (datetime): Fecha a formatear
        format_type (str): Tipo de formato (short, long, iso)
        
    Returns:
        str: Fecha formateada
    """
    if not date_obj:
        return ""
    
    formats = {
        'short': '%d/%m/%Y',
        'long': '%d de %B de %Y',
        'iso': '%Y-%m-%d',
        'datetime': '%d/%m/%Y %H:%M'
    }
    
    try:
        return date_obj.strftime(formats.get(format_type, formats['short']))
    except (AttributeError, ValueError):
        return str(date_obj)
```

### Sanitización
```python
import html
import bleach

def sanitize_input(text, allow_html=False):
    """
    Sanitiza entrada de texto
    
    Args:
        text (str): Texto a sanitizar
        allow_html (bool): Si permitir HTML básico
        
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""
    
    # Convertir a string si no lo es
    text = str(text).strip()
    
    if allow_html:
        # Permitir solo HTML seguro
        allowed_tags = ['p', 'br', 'strong', 'em', 'u']
        text = bleach.clean(text, tags=allowed_tags, strip=True)
    else:
        # Escapar todo HTML
        text = html.escape(text)
    
    return text

def clean_filename(filename):
    """
    Limpia nombre de archivo para almacenamiento seguro
    
    Args:
        filename (str): Nombre de archivo
        
    Returns:
        str: Nombre limpio
    """
    if not filename:
        return "unnamed_file"
    
    # Remover caracteres peligrosos
    clean_name = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Evitar nombres muy largos
    if len(clean_name) > 100:
        name, ext = clean_name.rsplit('.', 1) if '.' in clean_name else (clean_name, '')
        clean_name = f"{name[:95]}.{ext}" if ext else name[:100]
    
    return clean_name
```

### Helpers de Sistema
```python
import os
import uuid
from datetime import datetime, timedelta

def generate_unique_id():
    """
    Genera un ID único
    
    Returns:
        str: ID único
    """
    return str(uuid.uuid4())

def generate_filename(original_name, prefix="file"):
    """
    Genera nombre único para archivo
    
    Args:
        original_name (str): Nombre original
        prefix (str): Prefijo para el archivo
        
    Returns:
        str: Nombre único
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:8]
    
    # Obtener extensión
    if '.' in original_name:
        _, ext = original_name.rsplit('.', 1)
        return f"{prefix}_{timestamp}_{random_suffix}.{ext}"
    else:
        return f"{prefix}_{timestamp}_{random_suffix}"

def ensure_directory(path):
    """
    Asegura que un directorio existe
    
    Args:
        path (str): Ruta del directorio
        
    Returns:
        bool: True si existe o se creó exitosamente
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

def calculate_age(birth_date):
    """
    Calcula edad basada en fecha de nacimiento
    
    Args:
        birth_date (datetime): Fecha de nacimiento
        
    Returns:
        int: Edad en años
    """
    if not birth_date:
        return 0
    
    today = datetime.now().date()
    if hasattr(birth_date, 'date'):
        birth_date = birth_date.date()
    
    age = today.year - birth_date.year
    
    # Ajustar si no ha cumplido años este año
    if today < birth_date.replace(year=today.year):
        age -= 1
    
    return max(0, age)
```

### Cache Utilities
```python
import hashlib
import json

def generate_cache_key(*args, **kwargs):
    """
    Genera clave de cache basada en argumentos
    
    Args:
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
        
    Returns:
        str: Clave de cache
    """
    # Crear string único basado en argumentos
    cache_string = f"{args}_{sorted(kwargs.items())}"
    
    # Generar hash MD5
    return hashlib.md5(cache_string.encode()).hexdigest()

def serialize_for_cache(data):
    """
    Serializa datos para almacenamiento en cache
    
    Args:
        data: Datos a serializar
        
    Returns:
        str: Datos serializados
    """
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data)

def deserialize_from_cache(cached_data):
    """
    Deserializa datos desde cache
    
    Args:
        cached_data (str): Datos cacheados
        
    Returns:
        object: Datos deserializados
    """
    try:
        return json.loads(cached_data)
    except (json.JSONDecodeError, TypeError):
        return cached_data
```

## 🔍 Logging Utilities

### Configuración de Logging
```python
import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura logger personalizado
    
    Args:
        name (str): Nombre del logger
        log_file (str): Archivo de log (opcional)
        level: Nivel de logging
        
    Returns:
        Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_user_action(user_id, action, details=None):
    """
    Registra acción del usuario
    
    Args:
        user_id (str): ID del usuario
        action (str): Acción realizada
        details (dict): Detalles adicionales
    """
    logger = logging.getLogger('user_actions')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details or {}
    }
    
    logger.info(json.dumps(log_entry, ensure_ascii=False))
```

## 🧪 Testing Utilities

### Helpers para Testing
```python
def create_test_ticket(**kwargs):
    """
    Crea ticket de prueba con datos por defecto
    
    Args:
        **kwargs: Atributos personalizados
        
    Returns:
        dict: Datos del ticket de prueba
    """
    default_data = {
        'document_client': '12345678',
        'product_code': 'TEST001',
        'IMEI': '123456789012345',
        'reference': 'Test Product',
        'priority': 'Media',
        'state': 'Sin asignar',
        'type_of_service': '0',
        'city': 'Bogotá'
    }
    
    default_data.update(kwargs)
    return default_data

def mock_user_session(roles=None):
    """
    Crea sesión de usuario simulada para testing
    
    Args:
        roles (list): Roles del usuario
        
    Returns:
        dict: Datos de sesión
    """
    return {
        'user_id': 'test_user',
        'user_roles': roles or ['Admin'],
        'user_name': 'Test User'
    }
```

---

*Documentación del módulo Utils - Sistema de Tickets v2.1.0* 