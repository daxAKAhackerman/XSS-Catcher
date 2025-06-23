import pytest
from app import create_app, db
from app.schemas import init_app
from flask import Flask


class TestConfig:
    SECRET_KEY = "A_KEY_ONLY_USED_FOR_TESTS"
    SQLALCHEMY_DATABASE_URI = "postgresql://testing:testing@localhost:5433/testing"
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
def client_tester(app: Flask):
    return app.test_client()


@pytest.fixture()
def app_no_init():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client_tester_no_init(app_no_init: Flask):
    return app_no_init.test_client()
