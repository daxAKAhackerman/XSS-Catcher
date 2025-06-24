from typing import Iterator

import pytest
from app import create_app, db
from app.schemas import init_app
from flask import Flask
from flask.testing import FlaskClient


class TestConfig:
    SECRET_KEY = "A_KEY_ONLY_USED_FOR_TESTS"
    SQLALCHEMY_DATABASE_URI = "postgresql://testing:testing@localhost:5433/testing"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 300


@pytest.fixture()
def app(request: pytest.FixtureRequest) -> Iterator[Flask]:
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()

        if "no_db_init" not in request.keywords:
            init_app(app)

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client_tester(app: Flask) -> FlaskClient:
    return app.test_client()
