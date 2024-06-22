import os
import random
import string


def get_db_url() -> str:
    return f'postgresql:///{os.getenv("POSTGRES_DB", "postgres")}'


class Config:
    SECRET_KEY = "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    SQLALCHEMY_DATABASE_URI = get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300

    def __init__(self):
        if os.getenv("FLASK_DEBUG"):
            self.SECRET_KEY = "A_KEY_ONLY_USED_FOR_DEV"
            self.JWT_ACCESS_TOKEN_EXPIRES = 3600
