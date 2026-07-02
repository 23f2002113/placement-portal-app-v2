from flask_sqlalchemy import SQLAlchemy
from flask_security.core import Security
from flask_cors import CORS

db = SQLAlchemy()
security = Security()
cors = CORS()