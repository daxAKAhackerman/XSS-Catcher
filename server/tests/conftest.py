import os

import pytest
from app import create_app, db
from app.models import init_app


class TestConfig:
    SECRET_KEY = "A_KEY_ONLY_USED_FOR_TESTS"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "app-test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300


@pytest.fixture()
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()

        init_app(app)

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
