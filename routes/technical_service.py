# routes/technical_service.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from decimal import Decimal
from datetime import datetime
import pytz
from sqlalchemy.orm.attributes import flag_modified
import json
# Importa las funciones desde el módulo de servicios
from services.queries import get_product_information, get_sertec, get_spare_name, get_technicians, get_spare_parts, get_client_by_document, get_spare_parts_with_price, search_spare_parts_query, execute_query
from services.ticket_email_service import TicketEmailService
from services.problems_service import get_fresh_problems, get_problems_by_ids
# Importa los modelos
from models.employees import Empleados
from models.tickets import Tickets
from models import db
from models.problems import Problems
from models.sparesTickets import Spares_tickets
from routes.onedrive import refresh_token, get_ticket_images, delete_onedrive_images
from utils.access_control import role_required
from flask_login import login_required
from services.pagination_service import get_paginated_technical_service

technical_service_bp = Blueprint(
    "technical_service", __name__, template_folder="templates")

# Datos mock para tickets (con id_ticket y campos realistas)
MOCK_TICKETS = [
    {
        "id_ticket": 1,
        "cliente": "Juan Pérez",
        "estado": "Pendiente",
        "producto": "Celular Samsung A32",
        "fecha": "2025-07-23",
        "technical_name": "Carlos Técnico",
        "technical_document": "12345678",
        "state": "Pendiente",
        "priority": "Alta",
        "city": "Medellín",
        "reference": "A32-2025",
        "product_code": "SAMA32-2025",
        "IMEI": "356789123456789",
        "problems": ["No enciende", "Pantalla rota"],
        "spare_value": 120000,
        "service_value": 80000,
        "total": 200000,
        "comment": "Cliente reporta que el equipo no enciende tras caída.",
        "client": {
            "nombre": "Juan",
            "apellido1": "Pérez",
            "apellido2": "Gómez",
            "document": "123456789",
            "phone": "555-1234",
            "email": "juan.perez@email.com"
        }
    },
    {
        "id_ticket": 2,
        "cliente": "Ana Gómez",
        "estado": "Terminado",
        "producto": "Tablet Lenovo Tab M10",
        "fecha": "2025-07-22",
        "technical_name": "Laura Técnica",
        "technical_document": "87654321",
        "state": "Terminado",
        "priority": "Media",
        "city": "Bogotá",
        "reference": "M10-2025",
        "product_code": "LENM10-2025",
        "IMEI": "987654321098765",
        "problems": ["No carga"],
        "spare_value": 50000,
        "service_value": 60000,
        "total": 110000,
        "comment": "Se cambió el puerto de carga y se probó funcionamiento.",
        "client": {
            "nombre": "Ana",
            "apellido1": "Gómez",
            "apellido2": "Ruiz",
            "document": "987654321",
            "phone": "555-5678",
            "email": "ana.gomez@email.com"
        }
    }
]

@technical_service_bp.route("/technical_service")
def list_tickets():
    # Usar datos mock
    tickets = MOCK_TICKETS
    pagination = {"page": 1, "pages": 1, "per_page": 20, "total": len(tickets)}
    technicians = ["Técnico 1", "Técnico 2"]
    current_filters = {"search": "", "state": "", "city": ""}
    return render_template(
        "technical_service.html",
        tickets=tickets,
        pagination=pagination,
        technicians=technicians,
        current_filters=current_filters
    )

@technical_service_bp.route("/create_ticket", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        flash("Ticket creado (mock)", "success")
        return redirect(url_for("technical_service.list_tickets"))
    return render_template("create_ticket.html")

@technical_service_bp.route("/edit_ticket/<int:ticket_id>", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    ticket = next((t for t in MOCK_TICKETS if t["id_ticket"] == ticket_id), None)
    if not ticket:
        flash("Ticket no encontrado (mock)", "danger")
        return redirect(url_for("technical_service.list_tickets"))
    client = {
        "nombre": "Cliente Demo",
        "apellido1": "Apellido",
        "apellido2": "Demo",
        "document": "123456789",
        "phone": "555-1234",
        "email": "demo@cliente.com"
    }
    if request.method == "POST":
        flash("Ticket editado (mock)", "success")
        return redirect(url_for("technical_service.list_tickets"))
    return render_template("edit_ticket.html", ticket=ticket, client=client)

@technical_service_bp.route("/view_detail_ticket/<int:ticket_id>", methods=["GET"])
def view_detail_ticket(ticket_id):
    ticket = next((t for t in MOCK_TICKETS if t["id_ticket"] == ticket_id), None)
    if not ticket:
        flash("Ticket no encontrado (mock)", "danger")
        return redirect(url_for("technical_service.list_tickets"))
    client = ticket.get("client", {
        "nombre": "Cliente Demo",
        "apellido1": "Apellido",
        "apellido2": "Demo",
        "document": "123456789",
        "phone": "555-1234",
        "email": "demo@cliente.com"
    })
    spare_tickets = [
        {"spare_code": "BAT-A32", "quantity": 1, "unit_price": 60000, "total_price": 60000},
        {"spare_code": "PANTALLA-A32", "quantity": 1, "unit_price": 60000, "total_price": 60000}
    ] if ticket_id == 1 else [
        {"spare_code": "PUERTO-M10", "quantity": 1, "unit_price": 50000, "total_price": 50000}
    ]
    return render_template("view_detail_ticket.html", ticket=ticket, client=client, spare_tickets=spare_tickets)


# NOTA: El endpoint update_ticket_status_ajax ha sido centralizado en internal_repair.py
# Todos los módulos ahora usan el endpoint unificado: /tickets/update_ticket_status_ajax


@technical_service_bp.route('/send_email_notification/<int:ticket_id>', methods=['POST'])
def send_email_notification(ticket_id):
    """Envía una notificación por correo electrónico al cliente sobre el ticket Terminado"""
    ticket = Tickets.query.get_or_404(ticket_id)

    # Verificar que el ticket esté Terminado
    if ticket.state != "Terminado" and ticket.state != "Terminado":
        flash("El ticket debe estar Terminado para enviar la notificación", "warning")
        return redirect(url_for('technical_service.view_detail_ticket', ticket_id=ticket_id))

    # Obtener información necesaria
    cliente = get_client_by_document(ticket.document_client)
    tecnico = Empleados.query.filter_by(
        cedula=ticket.technical_document).first()
    problemas = ticket.problems

    # Verificar que el cliente tenga correo
    if not cliente.mail:
        flash(
            "El cliente no tiene una dirección de correo electrónico registrada", "warning")
        return redirect(url_for('technical_service.view_detail_ticket', ticket_id=ticket_id))

    # Enviar correo
    email_service = current_app.ticket_email_service
    success, error = email_service.enviar_notificacion_reparacion(
        cliente=cliente,
        ticket=ticket,
        problemas=problemas,
        tecnico=tecnico
    )

    if success:
        # Redirigir a la página de detalle con parámetro de éxito
        return redirect(url_for('technical_service.view_detail_ticket', ticket_id=ticket_id, email_sent='success'))
    else:
        # Redirigir con parámetro de error
        current_app.logger.error(f"Error al enviar el correo: {error}")
        return redirect(url_for('technical_service.view_detail_ticket', ticket_id=ticket_id, email_sent='error'))

@technical_service_bp.route("/search_products", methods=["POST"])
def search_products():
    """
    Ruta para buscar productos basados en un término de búsqueda.
    Similar a la búsqueda de repuestos pero para productos.
    """
    search_term = request.form.get('search', '')
    
    if not search_term or len(search_term) < 3:
        return jsonify({'products': []})
    
    # Obtener todos los productos
    all_products = get_product_information()
    
    # Filtrar productos basados en el término de búsqueda
    filtered_products = []
    search_term = search_term.lower()
    
    for product in all_products:
        code = product['CODIGO'].lower()
        description = product['DESCRIPCIO'].lower()
        
        if search_term in code or search_term in description:
            filtered_products.append(product)
    
    # Ordenar resultados para que los más relevantes aparezcan primero
    # (los que comienzan con el término de búsqueda)
    def sort_key(product):
        code = product['CODIGO'].lower()
        description = product['DESCRIPCIO'].lower()
        
        if code.startswith(search_term):
            return 0
        elif description.startswith(search_term):
            return 1
        else:
            return 2
    
    filtered_products.sort(key=sort_key)
    
    return jsonify({'products': filtered_products})

# Ruta original para búsqueda de repuestos (para compatibilidad)
@technical_service_bp.route("/search_spare_parts", methods=["POST"])
def search_spare_parts_original():
    """
    Ruta original para búsqueda de repuestos.
    Mantiene compatibilidad con código antiguo.
    """
    # Redirigir a la nueva implementación
    search_term = request.form.get("search", "").strip().lower()
    
    if not search_term or len(search_term) < 3:
        return jsonify({
            "success": False,
            "message": "Ingrese al menos 3 caracteres para buscar"
        }), 400
    
    try:
        # Usar la misma lógica que en la nueva implementación
        query = '''
        SELECT CODIGO, DESCRIPCIO
        FROM MTMERCIA
        WHERE CODLINEA = 'ST' AND 
        (LOWER(CODIGO) LIKE ? OR LOWER(DESCRIPCIO) LIKE ?)
        ORDER BY 
            CASE 
                WHEN LOWER(CODIGO) = ? THEN 1
                WHEN LOWER(CODIGO) LIKE ? THEN 2
                WHEN LOWER(DESCRIPCIO) = ? THEN 3
                WHEN LOWER(DESCRIPCIO) LIKE ? THEN 4
                ELSE 5
            END
        '''
        
        results = execute_query(query, (f'%{search_term}%', f'%{search_term}%', search_term, f'{search_term}%', search_term, f'{search_term}%'))
        
        spare_parts = []
        for row in results:
            if len(spare_parts) >= 30:
                break
                
            spare_parts.append({
                "code": row[0].strip() if row[0] else "",
                "description": row[1].strip() if row[1] else ""
            })
        
        if not spare_parts:
            return jsonify({
                "success": True,
                "parts": [],
                "count": 0,
                "message": "No se encontraron repuestos con ese criterio"
            })
            
        return jsonify({
            "success": True,
            "parts": spare_parts,
            "count": len(spare_parts)
        })
    
    except Exception as e:
        print(f"Error al buscar repuestos: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error al buscar repuestos: {str(e)}"
        }), 500


@technical_service_bp.route("/search_tickets", methods=["POST"])
def search_tickets():
    """
    Endpoint para búsqueda completa de tickets de servicio técnico sin limitaciones de paginado
    """
    try:
        search_term = request.form.get("search", "").strip()
        
        # Validar término de búsqueda
        from apps.tickets.services.search_service import SearchService
        validation = SearchService.validate_search_term(search_term)
        
        if not validation['is_valid']:
            return jsonify({
                "status": "error", 
                "message": validation['message']
            })
        
        # Realizar búsqueda
        tickets = SearchService.search_technical_service(search_term)
        summary = SearchService.get_search_summary(search_term, ticket_type="0")
        
        # Renderizar plantilla parcial con los resultados
        html_content = render_template(
            'partials/tickets_table_rows.html', 
            tickets=tickets
        )
        
        return jsonify({
            "status": "success", 
            "html": html_content,
            "summary": summary,
            "total_results": len(tickets),
            "search_term": search_term,
            "message": f"Se encontraron {len(tickets)} resultado(s) para '{search_term}'"
        })
    
    except Exception as e:
        current_app.logger.error(f"Error en búsqueda de tickets: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Error en búsqueda: {str(e)}"
        })
