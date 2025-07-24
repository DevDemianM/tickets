from flask import Blueprint, render_template, jsonify

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

@dashboard_bp.route("/dashboard", endpoint="dashboard")
def dashboard():
    # Datos mock para el dashboard
    metrics = {
        "tickets_activos": 5,
        "tickets_totales": 20,
        "garantias_activas": 2,
        "tiempo_promedio": 3.5,
        "valor_servicios": 1500000,
        "valor_repuestos": 500000,
    }
    return render_template("dashboard.html", metrics=metrics)

@dashboard_bp.route("/dashboard/metrics", methods=["GET"])
def get_dashboard_metrics():
    # Datos mock para métricas
    return jsonify({
        "active_tickets": 5,
        "total_tickets": 20,
        "active_warranties": 2,
        "avg_resolution_time_days": 3.5,
        "total_service_value": 1500000,
        "total_spare_value": 500000,
        "state_distribution": {"Pendiente": 3, "Terminado": 2},
        "type_distribution": {"ST": 10, "RI": 5, "GA": 5},
    })
