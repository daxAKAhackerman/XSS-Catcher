from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)



    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

from app import models

if models.User.query.filter_by(username='admin').first() == None:
    
    user = models.User('admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()