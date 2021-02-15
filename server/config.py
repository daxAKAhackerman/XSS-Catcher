import os
import random
import string

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get("POSTGRES_DB") and os.environ.get("POSTGRES_USER") and os.environ.get("POSTGRES_PASSWORD") and os.environ.get("POSTGRES_HOSTNAME"):
    DATABASE_URL = f'postgres://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOSTNAME")}/{os.environ.get("POSTGRES_DB")}'
else:
    DATABASE_URL = "sqlite:///" + os.path.join(basedir, "app.db")


class Config(object):
    SECRET_KEY = "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["refresh"]
