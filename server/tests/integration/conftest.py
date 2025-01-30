from typing import Iterator, cast

import pytest
from database import get_session
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models.auth import BlockedJti
from models.user import User
from sqlmodel import Session, delete
from sqlmodel.sql.expression import Select


@pytest.fixture()
def main_app() -> Iterator[FastAPI]:
    from main import app

    yield app


@pytest.fixture()
def test_client(main_app: FastAPI) -> Iterator[TestClient]:
    yield TestClient(main_app)


@pytest.fixture(autouse=True)
def setup_db() -> Iterator[Session]:
    session = next(get_session())
    yield session

    session.exec(cast(Select, delete(User)))
    session.exec(cast(Select, delete(BlockedJti)))
    session.commit()
