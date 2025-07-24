from flask import Blueprint, session, redirect, url_for, flash

tickets = Blueprint('tickets', __name__, template_folder='templates', static_folder='static')

@tickets.before_request
def check_service_tech_access():
    user_roles = session.get('user_roles', [])
    if 'servicioTecnico' not in user_roles and 'Admin' not in user_roles and 'jefeTienda' not in user_roles and 'posventa' not in user_roles:
        flash('Acceso denegado. Se requiere ser técnico de servicio, administrador o pos-venta.', 'danger')
        return redirect(url_for('home'))
# Importar la función para registrar blueprints
from apps.tickets.routes import register_blueprints

# Registrar todos los blueprints secundarios
from apps.tickets.routes.internal_repair import internal_repair_bp
from apps.tickets.routes.technical_service import technical_service_bp
from apps.tickets.routes.warranty import warranty_bp
from apps.tickets.routes.view_technical import view_technical_bp
from apps.tickets.routes.upload_images import upload_images_bp
from apps.tickets.routes.onedrive import onedrive_bp
from apps.tickets.routes.auth import auth_bp
from apps.tickets.routes.dashboard import dashboard_bp

# Registrar cada blueprint con el blueprint principal
tickets.register_blueprint(internal_repair_bp)
tickets.register_blueprint(technical_service_bp)
tickets.register_blueprint(warranty_bp)
tickets.register_blueprint(view_technical_bp)
tickets.register_blueprint(upload_images_bp)
tickets.register_blueprint(onedrive_bp)
tickets.register_blueprint(dashboard_bp)
