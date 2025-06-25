import os
import uuid


def get_db_url() -> str:
    if os.getenv("FLASK_DEBUG"):
        # In dev, rely on username/password auth and use TCP/IP
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    else:
        # In prod, rely on peer/trust auth and use Unix domain socket
        return "postgresql://postgres@/postgres"


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI = get_db_url()


class ProdConfig(BaseConfig):
    SECRET_KEY = str(uuid.uuid4())
    JWT_ACCESS_TOKEN_EXPIRES: int = 300


class DevConfig(BaseConfig):
    SECRET_KEY = "A_KEY_ONLY_USED_FOR_DEV"
    JWT_ACCESS_TOKEN_EXPIRES = 3600


def get_config() -> type:
    if os.getenv("FLASK_DEBUG"):
        return DevConfig
    else:
        return ProdConfig
