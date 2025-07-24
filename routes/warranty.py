from flask import Blueprint, render_template, request, redirect, url_for, flash

warranty_bp = Blueprint("warranty", __name__, template_folder="templates")

MOCK_WARRANTIES = [
    {
        "id_warranty": 1,
        "cliente": "Carlos Ruiz",
        "estado": "Activa",
        "producto": "Laptop HP 250 G7",
        "fecha": "2025-07-20",
        "problems": ["No enciende", "Batería dañada"],
        "spare_value": 90000,
        "service_value": 0,
        "total": 90000,
        "comment": "Equipo no enciende tras caída.",
        "client": {
            "nombre": "Carlos",
            "apellido1": "Ruiz",
            "apellido2": "Martínez",
            "document": "111222333",
            "phone": "555-1111",
            "email": "carlos.ruiz@email.com"
        },
        "spare_tickets": [
            {"spare_code": "BATERIA-HP250", "quantity": 1, "unit_price": 90000, "total_price": 90000}
        ]
    },
    {
        "id_warranty": 2,
        "cliente": "Lucía Torres",
        "estado": "Cerrada",
        "producto": "Celular Xiaomi Redmi 9",
        "fecha": "2025-07-18",
        "problems": ["Pantalla rota"],
        "spare_value": 120000,
        "service_value": 0,
        "total": 120000,
        "comment": "Pantalla reemplazada en garantía.",
        "client": {
            "nombre": "Lucía",
            "apellido1": "Torres",
            "apellido2": "López",
            "document": "444555666",
            "phone": "555-2222",
            "email": "lucia.torres@email.com"
        },
        "spare_tickets": [
            {"spare_code": "PANTALLA-REDMI9", "quantity": 1, "unit_price": 120000, "total_price": 120000}
        ]
    }
]

@warranty_bp.route("/warranty")
def list_warranties():
    warranties = MOCK_WARRANTIES
    pagination = {"page": 1, "pages": 1, "per_page": 20, "total": len(warranties)}
    return render_template("warranty.html", warranties=warranties, pagination=pagination)

@warranty_bp.route("/create_warranty", methods=["GET", "POST"])
def create_warranty():
    if request.method == "POST":
        flash("Garantía creada (mock)", "success")
        return redirect(url_for("warranty.list_warranties"))
    return render_template("create_warranty.html")

@warranty_bp.route("/edit_warranty/<int:warranty_id>", methods=["GET", "POST"])
def edit_warranty(warranty_id):
    warranty = next((w for w in MOCK_WARRANTIES if w["id_warranty"] == warranty_id), None)
    if not warranty:
        flash("Garantía no encontrada (mock)", "danger")
        return redirect(url_for("warranty.list_warranties"))
    client = warranty.get("client", {})
    if request.method == "POST":
        flash("Garantía editada (mock)", "success")
        return redirect(url_for("warranty.list_warranties"))
    return render_template("edit_warranty.html", warranty=warranty, client=client)

@warranty_bp.route("/view_detail_warranty/<int:warranty_id>", methods=["GET"])
def view_detail_warranty(warranty_id):
    warranty = next((w for w in MOCK_WARRANTIES if w["id_warranty"] == warranty_id), None)
    if not warranty:
        flash("Garantía no encontrada (mock)", "danger")
        return redirect(url_for("warranty.list_warranties"))
    client = warranty.get("client", {})
    spare_tickets = warranty.get("spare_tickets", [])
    return render_template("view_detail_warranty.html", warranty=warranty, client=client, spare_tickets=spare_tickets)
