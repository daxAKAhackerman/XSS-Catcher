import os
import random
import string

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get("POSTGRES_DB") and os.environ.get("POSTGRES_USER") and os.environ.get("POSTGRES_PASSWORD") and os.environ.get("POSTGRES_HOSTNAME"):
    DATABASE_URL = f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOSTNAME")}/{os.environ.get("POSTGRES_DB")}'
else:
    DATABASE_URL = "sqlite:///" + os.path.join(basedir, "app.db")


class Config:
    SECRET_KEY = "A_KEY_ONLY_USED_FOR_DEV" if os.getenv("FLASK_DEBUG") else "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300
