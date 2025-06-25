from typing import Optional

from config import get_config
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()
jwt = JWTManager()
cors = CORS()


def create_app(config_class: Optional[type] = None):
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())

    print(app.config.get("SECRET_KEY"))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/x/*": {"origins": "*"}})

    from app.api.auth import auth_bp
    from app.api.client import client_bp
    from app.api.settings import settings_bp
    from app.api.user import user_bp
    from app.api.x import x_bp
    from app.api.xss import xss_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(x_bp)
    app.register_blueprint(xss_bp)

    return app
