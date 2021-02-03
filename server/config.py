import os
import string
import random

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('POSTGRES_DB') and \
   os.environ.get('POSTGRES_USER') and \
   os.environ.get('POSTGRES_PASSWORD') and\
   os.environ.get('POSTGRES_HOSTNAME'):
    DATABASE_URL = f'postgres://${os.environ.get("POSTGRES_USER")}:${os.environ.get("POSTGRES_PASSWORD")}@${os.environ.get("POSTGRES_HOSTNAME")}/${os.environ.get("POSTGRES_DB")}'
else:
    DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'app.db')


class Config(object):
    SECRET_KEY = ''.join(random.choice(
        string.ascii_letters + string.digits) for i in range(32))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600
    REMEMBER_COOKIE_SAMESITE = 'Lax'
