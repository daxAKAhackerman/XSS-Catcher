from app import db
from app.models import Client
from flask.testing import FlaskClient


def login(client: FlaskClient, username: str, password: str) -> tuple[str, str]:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.json["access_token"], response.json["refresh_token"]


def create_client(name: str, owner_id: int = 1):
    new_client = Client(name=name, description="", owner_id=owner_id)
    new_client.gen_uid()
    db.session.add(new_client)
    db.session.commit()
