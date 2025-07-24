from flask import Flask
from routes import register_blueprints
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar la base de datos con SQLAlchemy
    db.init_app(app)

    # Registrar todos los blueprints de forma centralizada
    register_blueprints(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True) 