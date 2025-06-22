import os
import uuid


def get_db_url() -> str:
    if os.getenv("FLASK_DEBUG"):
        # In dev, rely on username/password auth and use TCP/IP
        return "postgresql://postgres:postgres@localhost:5432/postgres"
    else:
        # In prod, rely on peer/trust auth and use Unix domain socket
        return "postgresql://postgres@/postgres"


class Config:
    SECRET_KEY: str = str(uuid.uuid4())
    SQLALCHEMY_DATABASE_URI: str = get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    JWT_ACCESS_TOKEN_EXPIRES: int = 300

    def __init__(self) -> None:
        if os.getenv("FLASK_DEBUG"):
            # Prevent the cookie from going bad every time the server restarts and make it valid for a longer time
            self.SECRET_KEY = "A_KEY_ONLY_USED_FOR_DEV"
            self.JWT_ACCESS_TOKEN_EXPIRES = 3600
