# routes/auth.py

from flask import request, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from flask_bcrypt import Bcrypt
from models.employees import Empleados

bcrypt = Bcrypt()

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Acceso libre: redirige directamente al dashboard
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("tickets.auth.login"))
