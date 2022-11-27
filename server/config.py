import os
import random
import string


def get_db_url() -> str:
    basedir = os.path.abspath(os.path.dirname(__file__))
    sqlite_db_path = os.path.join(basedir, "app.db")

    if os.path.exists(sqlite_db_path) or os.getenv("FLASK_DEBUG"):
        return f"sqlite:///{sqlite_db_path}"
    else:
        with open(os.getenv("POSTGRES_PASSWORD_FILE"), "r") as file:
            pg_password = file.readline().rstrip()
        return f'postgresql://{os.getenv("POSTGRES_USER")}:{pg_password}@{os.getenv("POSTGRES_HOSTNAME")}/{os.getenv("POSTGRES_DB")}'


class Config:
    SECRET_KEY = "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    SQLALCHEMY_DATABASE_URI = get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300

    def __init__(self):
        if os.getenv("FLASK_DEBUG"):
            self.SECRET_KEY = "A_KEY_ONLY_USED_FOR_DEV"
