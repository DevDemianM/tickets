
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .employees import Empleados
from .problems import Problems
from .problemsTickets import Problems_tickets
from .tickets import Tickets
from .sparesTickets import Spares_tickets
