# Sistema de Gestión de Tickets de Servicio Técnico

## 📋 Información General

**Versión:** 2.1.0  
**Última actualización:** Enero 2025  
**Autor:** Equipo de Desarrollo Centralizado  
**Estado:** Producción  

---

## 🚀 Proyecto Independiente y Desplegable

Este proyecto es **totalmente independiente** y puede ejecutarse localmente o desplegarse fácilmente en Railway o cualquier plataforma compatible con Python.

- **Configuración por variables de entorno (.env)**
- **Estructura modular y profesional (Flask + Blueprints)**
- **Listo para producción y pruebas**

---

## 🛠️ Instalación y Configuración Rápida

### 1. Clona el repositorio
```bash
git clone <URL_DEL_REPO>
cd tickets
```

### 2. Crea y configura tu archivo `.env`
Copia el siguiente ejemplo y personaliza según tu entorno:
```env
SECRET_KEY=dev_secret_key
DATABASE_URL=sqlite:///tickets.db  # O tu cadena de conexión a SQL Server o PostgreSQL
# Variables opcionales para OneDrive, etc.
# CLIENT_ID=...
# CLIENT_SECRET=...
# REDIRECT_URI=...
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecuta la aplicación localmente
```bash
python app.py
```

La app estará disponible en [http://localhost:5000](http://localhost:5000)

---

## 🚢 Despliegue en Railway

1. **Sube tu código a GitHub**
2. **Crea un nuevo proyecto en Railway**
3. **Agrega las variables de entorno desde tu `.env`**
4. **Railway detectará el `Procfile` y lanzará la app automáticamente**

---

## 📦 Estructura del Proyecto

```
tickets/
├── app.py                # Punto de entrada principal
├── config.py             # Configuración centralizada
├── requirements.txt      # Dependencias
├── Procfile              # Comando para Railway
├── .env                  # Variables de entorno (NO subir a GitHub)
├── models/               # Modelos de datos
├── routes/               # Blueprints y endpoints
├── services/             # Lógica de negocio
├── templates/            # Vistas HTML
├── static/               # Archivos estáticos
├── utils/                # Utilidades
└── scripts/              # Herramientas y migraciones
```

---

## 🔑 Variables de Entorno Principales

- `SECRET_KEY`: Clave secreta Flask
- `DATABASE_URL`: Cadena de conexión a la base de datos (SQLite, PostgreSQL, SQL Server, etc.)
- (Opcional) `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`: Para integración con OneDrive

---

## 📚 Documentación de Módulos

- [`docs/models.md`](./docs/models.md) - Modelos de datos y estructura de BD
- [`docs/routes.md`](./docs/routes.md) - Endpoints y controladores
- [`docs/services.md`](./docs/services.md) - Lógica de negocio y servicios
- [`docs/templates.md`](./docs/templates.md) - Vistas y componentes UI
- [`docs/utils.md`](./docs/utils.md) - Utilidades y helpers

---

## 📝 Notas Importantes

- **No subas tu archivo `.env` a GitHub** (contiene información sensible)
- Puedes cambiar la base de datos fácilmente editando `DATABASE_URL` en `.env`
- El sistema soporta SQL Server, SQLite y PostgreSQL (ajusta dependencias si cambias de motor)
- Para producción, cambia el valor de `SECRET_KEY` y usa una base de datos robusta

---

*Documentación actualizada para la versión 2.1.0 - Enero 2025* 