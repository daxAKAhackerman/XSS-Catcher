from config import Config
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
cors = CORS()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    cors.init_app(app, resources={r"/x/*": {"origins": "*"}})

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app


from app import models
