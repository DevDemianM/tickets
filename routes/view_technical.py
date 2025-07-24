from flask import Blueprint, render_template, request, jsonify

view_technical_bp = Blueprint("view_technical", __name__, template_folder="templates")

MOCK_TECHNICAL_TICKETS = [
    {"id": 1, "cliente": "Juan Pérez", "estado": "Pendiente", "producto": "Celular", "fecha": "2025-07-23"},
    {"id": 2, "cliente": "Ana Gómez", "estado": "Terminado", "producto": "Tablet", "fecha": "2025-07-22"},
]

@view_technical_bp.route("/view_technical")
def view_technical():
    tickets = MOCK_TECHNICAL_TICKETS
    return render_template("view_technical.html", tickets=tickets)

@view_technical_bp.route("/view_technical/ticket/<int:ticket_id>", methods=["GET", "POST"])
def technician_ticket_detail(ticket_id):
    ticket = next((t for t in MOCK_TECHNICAL_TICKETS if t["id"] == ticket_id), None)
    if not ticket:
        return render_template("technician_ticket_detail.html", ticket=None)
    return render_template("technician_ticket_detail.html", ticket=ticket)

@view_technical_bp.route("/update_ticket_status", methods=["POST"])
def update_ticket_status():
    # Mock: simplemente retorna éxito
    return jsonify({'success': True, 'message': 'Estado actualizado (mock)'})

@view_technical_bp.route("/search_tickets", methods=["POST"])
def search_tickets():
    # Mock: retorna todos los tickets
    html_content = render_template('partials/view_technical_table_rows.html', tickets=MOCK_TECHNICAL_TICKETS)
    return jsonify({
        "status": "success",
        "html": html_content,
        "summary": {},
        "total_results": len(MOCK_TECHNICAL_TICKETS),
        "search_term": request.form.get("search", ""),
        "message": f"Se encontraron {len(MOCK_TECHNICAL_TICKETS)} ticket(s) asignado(s)"
    })
