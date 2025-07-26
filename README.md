# 🎫 Sistema de Gestión de Tickets de Servicio Técnico

<div align="center">

<<<<<<< HEAD
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.41-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-2.1.0-brightgreen.svg)

**Sistema completo de gestión de tickets para servicios técnicos con soporte multi-plataforma**

[🚀 Características](#-características) • [📦 Instalación](#-instalación) • [🔧 Configuración](#-configuración) • [📚 Documentación](#-documentación) • [🤝 Contribuir](#-contribuir)

</div>

=======
>>>>>>> 8a4e7ee1083a20b8ff5323194811883bff7e2805
---

## 📋 Tabla de Contenidos

- [🎯 Descripción](#-descripción)
- [✨ Características](#-características)
- [🛠️ Tecnologías](#️-tecnologías)
- [📦 Instalación](#-instalación)
- [🔧 Configuración](#-configuración)
- [🚀 Despliegue](#-despliegue)
- [📚 Documentación](#-documentación)
- [🏗️ Estructura del Proyecto](#️-estructura-del-proyecto)
- [🔑 Variables de Entorno](#-variables-de-entorno)
- [📝 API Endpoints](#-api-endpoints)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

---

## 🎯 Descripción

Sistema de gestión integral de tickets para servicios técnicos que permite manejar garantías, reparaciones internas y servicios técnicos de manera eficiente. Desarrollado con Flask y optimizado para producción.

### 🎯 Objetivos del Sistema

- ✅ **Gestión completa de tickets** (garantías, reparaciones internas, servicios técnicos)
- ✅ **Sistema de autenticación** seguro
- ✅ **Integración con OneDrive** para almacenamiento de archivos
- ✅ **Búsqueda avanzada** con filtros múltiples
- ✅ **Sistema de notificaciones** por email
- ✅ **Interfaz responsive** y moderna
- ✅ **Optimización de rendimiento** con índices de base de datos

---

## ✨ Características

### 🔧 Funcionalidades Principales

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| 🎫 **Tickets de Garantía** | Gestión completa de garantías con seguimiento | ✅ Activo |
| 🔧 **Reparaciones Internas** | Control de reparaciones internas y repuestos | ✅ Activo |
| 👨‍💼 **Servicios Técnicos** | Gestión de servicios técnicos externos | ✅ Activo |
| 📊 **Dashboard** | Panel de control con estadísticas | ✅ Activo |
| 🔍 **Búsqueda Avanzada** | Sistema de búsqueda unificado | ✅ Activo |
| 📧 **Notificaciones** | Sistema de emails automáticos | ✅ Activo |
| ☁️ **OneDrive Integration** | Almacenamiento en la nube | ✅ Activo |

### 🚀 Características Técnicas

- **Arquitectura Modular**: Blueprints de Flask para organización
- **Base de Datos Multi-Motor**: Soporte para SQLite, PostgreSQL, SQL Server
- **Optimización**: Índices de base de datos y consultas optimizadas
- **Seguridad**: Autenticación con bcrypt y sesiones seguras
- **Responsive**: Interfaz adaptativa para móviles y tablets
- **API RESTful**: Endpoints bien estructurados
- **Logging**: Sistema de logs para debugging

---

## 🛠️ Tecnologías

### Backend
- **Python 3.8+** - Lenguaje principal
- **Flask 3.1.1** - Framework web
- **SQLAlchemy 2.0.41** - ORM para base de datos
- **Flask-Login** - Sistema de autenticación
- **Flask-Bcrypt** - Encriptación de contraseñas

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript ES6+** - Interactividad
- **Bootstrap** - Framework CSS responsive
- **Jinja2** - Motor de plantillas

### Base de Datos
- **SQLite** - Desarrollo local
- **PostgreSQL** - Producción (recomendado)
- **SQL Server** - Compatibilidad empresarial

### Herramientas Adicionales
- **Gunicorn** - Servidor WSGI para producción
- **APScheduler** - Tareas programadas
- **Azure Communication** - Servicios de email
- **Office365-REST-Python-Client** - Integración OneDrive

---

## 📦 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/tickets.git
cd tickets
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración básica
SECRET_KEY=tu_clave_secreta_muy_segura
DATABASE_URL=sqlite:///tickets.db

# Configuración de email (opcional)
EMAIL_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_password

# OneDrive (opcional)
CLIENT_ID=tu_client_id
CLIENT_SECRET=tu_client_secret
REDIRECT_URI=http://localhost:5000/auth/callback
```

### 5. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## 🔧 Configuración

### Configuración de Base de Datos

#### SQLite (Desarrollo)
```env
DATABASE_URL=sqlite:///tickets.db
```

#### PostgreSQL (Producción)
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/tickets_db
```

#### SQL Server
```env
DATABASE_URL=mssql+pyodbc://usuario:password@servidor/base_datos?driver=ODBC+Driver+17+for+SQL+Server
```

### Configuración de Email

```env
EMAIL_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
```

### Configuración de OneDrive

1. Registra tu aplicación en [Azure Portal](https://portal.azure.com)
2. Obtén el Client ID y Client Secret
3. Configura las variables en `.env`

---

## 🚀 Despliegue

### Despliegue en Railway

1. **Fork del repositorio** en GitHub
2. **Conecta Railway** con tu repositorio
3. **Configura las variables de entorno** en Railway
4. **Deploy automático** con cada push

### Despliegue en Heroku

```bash
# Instalar Heroku CLI
heroku create tu-app-name
heroku config:set SECRET_KEY=tu_clave_secreta
heroku config:set DATABASE_URL=postgresql://...
git push heroku main
```

### Despliegue en VPS

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip nginx

# Configurar Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Configurar Nginx como proxy reverso
```

---

## 📚 Documentación

### 📖 Documentación de Módulos

- [📊 Modelos de Datos](./docs/models.md) - Estructura de la base de datos
- [🛣️ Rutas y Endpoints](./docs/routes.md) - API y controladores
- [⚙️ Servicios](./docs/services.md) - Lógica de negocio
- [🎨 Plantillas](./docs/templates.md) - Vistas y componentes UI
- [🔧 Utilidades](./docs/utils.md) - Herramientas y helpers

### 📋 Guías de Uso

#### Crear un Nuevo Ticket

1. Accede al dashboard
2. Selecciona el tipo de ticket (Garantía/Reparación/Servicio)
3. Completa el formulario con los datos requeridos
4. Adjunta archivos si es necesario
5. Guarda el ticket

#### Búsqueda Avanzada

- Usa el sistema de búsqueda unificado
- Aplica filtros por fecha, estado, tipo
- Exporta resultados a Excel

#### Gestión de Usuarios

- Sistema de roles y permisos
- Autenticación segura
- Control de acceso por módulos

---

## 🏗️ Estructura del Proyecto

```
tickets/
├── 📁 app.py                 # Punto de entrada principal
├── 📁 config.py              # Configuración centralizada
├── 📁 requirements.txt       # Dependencias del proyecto
├── 📁 Procfile              # Configuración para Railway
├── 📁 .env                  # Variables de entorno (NO subir)
├── 📁 README.md             # Documentación principal
│
├── 📁 models/               # Modelos de datos
│   ├── __init__.py
│   ├── employees.py         # Modelo de empleados
│   ├── problems.py          # Modelo de problemas
│   ├── tickets.py           # Modelo principal de tickets
│   ├── spares.py            # Modelo de repuestos
│   └── warranty.py          # Modelo de garantías
│
├── 📁 routes/               # Blueprints y endpoints
│   ├── __init__.py
│   ├── auth.py              # Autenticación
│   ├── dashboard.py         # Panel principal
│   ├── warranty.py          # Gestión de garantías
│   ├── internal_repair.py   # Reparaciones internas
│   ├── technical_service.py # Servicios técnicos
│   ├── onedrive.py          # Integración OneDrive
│   └── upload_images.py     # Subida de archivos
│
├── 📁 services/             # Lógica de negocio
│   ├── search_service.py    # Búsqueda avanzada
│   ├── ticket_email_service.py # Notificaciones
│   ├── cache_manager.py     # Gestión de caché
│   └── pagination_service.py # Paginación
│
├── 📁 templates/            # Vistas HTML
│   ├── base.html            # Plantilla base
│   ├── dashboard.html       # Panel principal
│   ├── warranty.html        # Gestión de garantías
│   └── partials/            # Componentes reutilizables
│
├── 📁 static/               # Archivos estáticos
│   ├── css/                 # Estilos CSS
│   ├── js/                  # JavaScript
│   └── images/              # Imágenes
│
├── 📁 utils/                # Utilidades
│   └── access_control.py    # Control de acceso
│
├── 📁 scripts/              # Herramientas y migraciones
│   ├── performance_monitor.py
│   └── apply_database_optimization.py
│
└── 📁 docs/                 # Documentación
    ├── models.md
    ├── routes.md
    ├── services.md
    └── templates.md
```

---

## 🔑 Variables de Entorno

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para Flask | `mi_clave_secreta_2025` |
| `DATABASE_URL` | URL de conexión a BD | `sqlite:///tickets.db` |

### Variables Opcionales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `EMAIL_SERVER` | Servidor SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Puerto SMTP | `587` |
| `EMAIL_USER` | Usuario de email | `admin@empresa.com` |
| `EMAIL_PASSWORD` | Password de email | `app_password` |
| `CLIENT_ID` | OneDrive Client ID | `12345678-1234-1234-1234-123456789012` |
| `CLIENT_SECRET` | OneDrive Client Secret | `mi_client_secret` |
| `REDIRECT_URI` | OneDrive Redirect URI | `http://localhost:5000/auth/callback` |

---

## 📝 API Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/logout` - Cerrar sesión

### Dashboard
- `GET /dashboard` - Panel principal
- `GET /dashboard/stats` - Estadísticas

### Garantías
- `GET /warranty` - Listar garantías
- `POST /warranty/create` - Crear garantía
- `GET /warranty/<id>` - Ver garantía
- `PUT /warranty/<id>` - Actualizar garantía
- `DELETE /warranty/<id>` - Eliminar garantía

### Reparaciones Internas
- `GET /internal_repair` - Listar reparaciones
- `POST /internal_repair/create` - Crear reparación
- `GET /internal_repair/<id>` - Ver reparación
- `PUT /internal_repair/<id>` - Actualizar reparación

### Servicios Técnicos
- `GET /technical_service` - Listar servicios
- `POST /technical_service/create` - Crear servicio
- `GET /technical_service/<id>` - Ver servicio
- `PUT /technical_service/<id>` - Actualizar servicio

### Búsqueda
- `GET /search` - Búsqueda unificada
- `GET /search/export` - Exportar resultados

### OneDrive
- `GET /onedrive/auth` - Autenticación OneDrive
- `POST /onedrive/upload` - Subir archivo
- `GET /onedrive/files` - Listar archivos

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, sigue estos pasos:

### 🚀 Cómo Contribuir

1. **Fork del proyecto**
2. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit tus cambios** (`git commit -m 'Add some AmazingFeature'`)
4. **Push a la rama** (`git push origin feature/AmazingFeature`)
5. **Abre un Pull Request**

### 📋 Guías de Contribución

- Mantén el código limpio y bien documentado
- Sigue las convenciones de Python (PEP 8)
- Añade tests para nuevas funcionalidades
- Actualiza la documentación cuando sea necesario

### 🐛 Reportar Bugs

Si encuentras un bug, por favor:

1. Revisa si ya existe un issue similar
2. Crea un nuevo issue con:
   - Descripción detallada del problema
   - Pasos para reproducir
   - Información del entorno (OS, Python version, etc.)
   - Capturas de pantalla si es relevante

### 💡 Solicitar Features

Para solicitar nuevas funcionalidades:

1. Describe la feature en detalle
2. Explica por qué sería útil
3. Proporciona ejemplos de uso si es posible

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **Flask** por el excelente framework web
- **SQLAlchemy** por el ORM robusto
- **Bootstrap** por los componentes UI
- **Railway** por la plataforma de despliegue

---

<div align="center">

**Desarrollado con ❤️ por el Equipo de Desarrollo Centralizado**

*Versión 2.1.0 - Enero 2025*

[⬆️ Volver arriba](#-sistema-de-gestión-de-tickets-de-servicio-técnico)

</div> 
