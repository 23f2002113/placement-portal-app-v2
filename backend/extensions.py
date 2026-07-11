from flask_sqlalchemy import SQLAlchemy
from flask_security.core import Security
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery

db = SQLAlchemy()
security = Security()
cors = CORS()
mail = Mail()
celery = Celery()