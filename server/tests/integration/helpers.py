from typing import Generator, Optional

from fastapi.testclient import TestClient
from httpx._auth import Auth
from httpx._models import Request, Response
from models.user import User
from sqlmodel import Session


class BearerAuth(Auth):
    _auth_header: str

    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self._auth_header
        yield request

    def _build_auth_header(self, token: str) -> str:
        return f"Bearer {token}"


def create_user(
    session: Session, username: str = "admin", password: str = "admin", is_admin: bool = True, first_login: bool = False, mfa_secret: Optional[str] = None
) -> User:
    password_hash = User.hash_password(password)
    user = User(username=username, password_hash=password_hash, is_admin=is_admin, first_login=first_login, mfa_secret=mfa_secret)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def login(client: TestClient, username: str = "admin", password: str = "admin") -> tuple[str, str, BearerAuth]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    response_json = response.json()

    return response_json["access_token"], response_json["refresh_token"], BearerAuth(response_json["access_token"])
