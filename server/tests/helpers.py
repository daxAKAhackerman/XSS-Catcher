from app import db
from app.models import Client, User
from flask.testing import FlaskClient


def login(client_tester: FlaskClient, username: str, password: str) -> tuple[str, str]:
    response = client_tester.post("/api/auth/login", json={"username": username, "password": password})
    return response.json["access_token"], response.json["refresh_token"]


def create_client(name: str, owner_id: int = 1) -> Client:
    client = Client(name=name, description="", owner_id=owner_id)
    client.gen_uid()
    db.session.add(client)
    db.session.commit()
    return client


def create_user(username: str, password: str = "test") -> User:
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
