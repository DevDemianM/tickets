import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tickets.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 