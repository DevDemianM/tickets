from flask_login import UserMixin
from . import db

class Empleados(db.Model, UserMixin):
    __bind_key__ = "db2"
    __tablename__ = "empleados"
    __table_args__ = {
        'extend_existing': True  
    }
    
    id = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sede = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)
    jefeTienda = db.Column(db.Boolean, default=False)
    isSede = db.Column(db.Boolean, default=False)
    isTV = db.Column(db.Boolean, default=False)
    password_secret = db.Column(db.String(60))
    cedula = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)
    cargo = db.Column('cargo_new', db.String(25), db.ForeignKey('roles.nombre'))
    pass_encrip = db.Column(db.String(400))
