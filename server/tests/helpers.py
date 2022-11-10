from typing import Any, Dict, List

from app import db
from app.models import Client, Settings, User
from flask.testing import FlaskClient


def login(client_tester: FlaskClient, username: str, password: str) -> tuple[str, str]:
    response = client_tester.post("/api/auth/login", json={"username": username, "password": password})
    return response.json["access_token"], response.json["refresh_token"]


def create_client(name: str, owner_id: int = 1, webhook_url: str = None, mail_to: str = None) -> Client:
    client = Client(name=name, description="", owner_id=owner_id, webhook_url=webhook_url, mail_to=mail_to)
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


def set_settings(*args: List, **kwargs: Dict[str, Any]) -> Settings:
    current_settings = db.session.query(Settings).first()
    db.session.delete(current_settings)
    settings = Settings(id=1, **kwargs)
    db.session.add(settings)
    db.session.commit()
    return settings
