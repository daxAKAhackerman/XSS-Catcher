from typing import Iterator, Optional, cast

import pytest
from database import get_session
from fastapi.testclient import TestClient
from models.auth import BlockedJti
from models.user import User
from requests.auth import AuthBase
from sqlmodel import Session, delete
from sqlmodel.sql.expression import Select


class BearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


@pytest.fixture()
def test_client() -> Iterator[TestClient]:
    from main import app

    yield TestClient(app)


@pytest.fixture(autouse=True)
def setup_db() -> Iterator[Session]:
    session = next(get_session())
    yield session

    session.exec(cast(Select, delete(User)))
    session.exec(cast(Select, delete(BlockedJti)))
    session.commit()


def create_user(username: str = "admin", password: str = "admin", is_admin: bool = True, first_login: bool = False, mfa_secret: Optional[str] = None) -> User:
    session = next(get_session())
    password_hash = User.hash_password(password)
    user = User(username=username, password_hash=password_hash, is_admin=is_admin, first_login=first_login, mfa_secret=mfa_secret)
    session.add(user)
    session.commit()

    return user


def delete_user(user: User) -> None:
    session = next(get_session())
    session.delete(user)
    session.commit()


def login(client: TestClient, username: str = "admin", password: str = "admin") -> tuple[str, str, BearerAuth]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    response_json = response.json()

    return response_json["access_token"], response_json["refresh_token"], BearerAuth(response_json["access_token"])
