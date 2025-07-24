from datetime import datetime
from flask_login import UserMixin
import pytz
from sqlalchemy import case
from . import db
from models.problemsTickets import Problems_tickets
from models.sparesTickets import Spares_tickets


def get_colombia_utc_now():
    """
    FUNCIÓN HELPER: Obtiene la hora actual de Colombia y la convierte a UTC
    para guardar consistentemente en la base de datos
    """
    zona_bogota = pytz.timezone('America/Bogota')
    hora_colombia = datetime.now(tz=zona_bogota)
    return hora_colombia.astimezone(pytz.UTC).replace(tzinfo=None)


class Tickets(db.Model, UserMixin):
    __bind_key__ = "db4"
    __tablename__ = "Tickets"
    __table_args__ = {"schema": "plan_beneficios"}

    id_ticket = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    technical_name = db.Column(db.String(33), nullable=False)
    technical_document = db.Column(db.String(11), nullable=False)
    document_client = db.Column(db.String(11), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    IMEI = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.String(250), nullable=True)
    reference = db.Column(db.String(100), nullable=False)
    type_of_service = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(15), nullable=False)
    invoice_number = db.Column(db.String(25), nullable=True)
    creation_date = db.Column(
        db.DateTime, nullable=True, default=get_colombia_utc_now)
    assigned = db.Column(db.DateTime, nullable=True)
    in_progress = db.Column(db.DateTime, nullable=True)
    in_revision = db.Column(db.DateTime, nullable=True)
    finished = db.Column(db.DateTime, nullable=True)
    spare_value = db.Column(db.Numeric(12, 2), nullable=True, default=0.0)
    service_value = db.Column(db.Numeric(12, 2), nullable=True, default=0.0)
    discounted_value = db.Column(db.Numeric(12, 2), nullable=True, default=0.0)
    total = db.Column(db.Numeric(12, 2), nullable=True, default=0.0)

    # Usar la tabla directamente
    problems = db.relationship("Problems",
                               secondary=Problems_tickets.__table__,
                               backref=db.backref("tickets", lazy="dynamic"),
                               lazy="dynamic")

    def get_spare_parts(self):
        spare_tickets = Spares_tickets.query.filter_by(
            id_ticket=self.id_ticket).all()
        return spare_tickets

    def update_state(self, new_state):
        """Actualiza el estado del ticket y registra la hora del cambio"""
        self.state = new_state
        now = get_colombia_utc_now()  # ARREGLAR: Usar función helper de Colombia
        
        if new_state == "Sin asignar":
            # Para Sin asignar, no necesitamos actualizar ningún timestamp específico
            pass
        elif new_state == "Asignado":
            self.assigned = now
        elif new_state == "Reingreso":
            self.re_entry = now
        elif new_state == "En proceso":
            self.in_progress = now
        elif new_state == "En Revision":
            self.in_revision = now
            print(f"Actualizando in_revision con timestamp: {now}")
        elif new_state == "Terminado":
            self.finished = now
        
        return now

    @classmethod
    def get_latest_activity_expression(cls):
        """
        Genera una expresión SQL que calcula la fecha de actividad más reciente del ticket.
        
        Considera las siguientes fechas en orden de prioridad:
        1. finished (fecha de finalización)
        2. in_revision (fecha de revisión)  
        3. in_progress (fecha de progreso)
        4. assigned (fecha de asignación)
        5. creation_date (fecha de creación)
        
        Returns:
            Expresión SQL para usar en order_by()
        """
        return case(
            (cls.finished.isnot(None), cls.finished),
            (cls.in_revision.isnot(None), cls.in_revision),
            (cls.in_progress.isnot(None), cls.in_progress),
            (cls.assigned.isnot(None), cls.assigned),
            else_=cls.creation_date
        ).desc()
