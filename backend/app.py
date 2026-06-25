import uuid
from flask import Flask
from extensions import db
from models import *

from flask_security import hash_password

from resources import auth_blueprint

def create_app():
    app = Flask(__name__)

    ## Configuration
    app.config['SQL_ALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mad2.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SECURITY_PASSWORD_SALT'] = 'your-salt'
    app.config['SECURITY_PASSWORD_HASH']= 'argon2'

   
    db.init_app(app)

    ## Flask security part 
    from flask_security.datastore import SQLAlchemyUserDatastore
    from extensions import security
    datastore = SQLAlchemyUserDatastore(db, User, Role )
    security.init_app(app, datastore = datastore ) 

    app.datastore = datastore

    app.register_blueprint(auth_blueprint)


    with app.app_context():
        db.create_all()
        
        ## Create role tabel:
        if not datastore.find_role('admin'):
            datastore.create_role(name='admin', description='Superuser')

        if not datastore.find_role('company'):
            datastore.create_role(name='company', description='Recruiter')
            
        if not datastore.find_role('student'):
            datastore.create_role(name='student', description='Institute Student')
            
        ## Programmatically add admin details at the time of database creation.
        if not datastore.find_user(email='admin@gmail.com'):
            datastore.create_user(
                name="Admin",
                email="admin@gmail.com",
                password=hash_password("admin1234"),
                roles=["admin"] 
            )
            
        db.session.commit()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)