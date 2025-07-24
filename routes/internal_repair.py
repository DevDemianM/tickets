# routes/internal_repair.py

from flask import Blueprint, render_template, request, redirect, url_for, flash

internal_repair_bp = Blueprint("internal_repair", __name__, template_folder="templates")

MOCK_INTERNAL_REPAIRS = [
    {
        "id_repair": 1,
        "cliente": "Pedro López",
        "estado": "En proceso",
        "producto": "Impresora Epson L3150",
        "fecha": "2025-07-21",
        "problems": ["No imprime", "Atasco de papel"],
        "spare_value": 40000,
        "service_value": 70000,
        "total": 110000,
        "comment": "Cliente reporta que la impresora no imprime y atasca papel.",
        "client": {
            "nombre": "Pedro",
            "apellido1": "López",
            "apellido2": "Ramírez",
            "document": "222333444",
            "phone": "555-3333",
            "email": "pedro.lopez@email.com"
        },
        "spare_tickets": [
            {"spare_code": "CARTUCHO-EPSON", "quantity": 1, "unit_price": 40000, "total_price": 40000}
        ]
    },
    {
        "id_repair": 2,
        "cliente": "María Díaz",
        "estado": "Terminado",
        "producto": "Monitor LG 24MK400H",
        "fecha": "2025-07-19",
        "problems": ["No enciende"],
        "spare_value": 0,
        "service_value": 50000,
        "total": 50000,
        "comment": "Se revisó y se cambió el fusible.",
        "client": {
            "nombre": "María",
            "apellido1": "Díaz",
            "apellido2": "García",
            "document": "555666777",
            "phone": "555-4444",
            "email": "maria.diaz@email.com"
        },
        "spare_tickets": []
    }
]

@internal_repair_bp.route("/internal_repair")
def internal_repair():
    repairs = MOCK_INTERNAL_REPAIRS
    pagination = {"page": 1, "pages": 1, "per_page": 20, "total": len(repairs)}
    return render_template("internal_repair.html", repairs=repairs, pagination=pagination)

@internal_repair_bp.route("/create_ticketsRI", methods=["GET", "POST"])
def create_ticketsRI():
    if request.method == "POST":
        flash("Reparación interna creada (mock)", "success")
        return redirect(url_for("internal_repair.internal_repair"))
    return render_template("create_ticketsRI.html")

@internal_repair_bp.route("/edit_tickets_RI/<int:repair_id>", methods=["GET", "POST"])
def edit_tickets_RI(repair_id):
    repair = next((r for r in MOCK_INTERNAL_REPAIRS if r["id_repair"] == repair_id), None)
    if not repair:
        flash("Reparación interna no encontrada (mock)", "danger")
        return redirect(url_for("internal_repair.internal_repair"))
    client = repair.get("client", {})
    if request.method == "POST":
        flash("Reparación interna editada (mock)", "success")
        return redirect(url_for("internal_repair.internal_repair"))
    return render_template("edit_tickets_RI.html", repair=repair, client=client)

@internal_repair_bp.route("/detail_RI/<int:repair_id>", methods=["GET"])
def detail_RI(repair_id):
    repair = next((r for r in MOCK_INTERNAL_REPAIRS if r["id_repair"] == repair_id), None)
    if not repair:
        flash("Reparación interna no encontrada (mock)", "danger")
        return redirect(url_for("internal_repair.internal_repair"))
    client = repair.get("client", {})
    spare_tickets = repair.get("spare_tickets", [])
    return render_template("detail_RI.html", repair=repair, client=client, spare_tickets=spare_tickets)
