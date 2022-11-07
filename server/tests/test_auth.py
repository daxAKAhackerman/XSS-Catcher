from app import db
from app.models import Blocklist
from flask.testing import FlaskClient
from tests.helpers import login


def test__login__given_credentials__when_already_authenticated__then_400_returned(client: FlaskClient):
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/auth/login", json={"username": "test", "password": "test"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Already logged in"}
    assert response.status_code == 400


def test__login__given_credentials__when_password_is_wrong__then_403_returned(client: FlaskClient):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "bad"})
    assert response.json == {"msg": "Bad username or password"}
    assert response.status_code == 403


def test__login__given_credentials__when_credentials_are_valid__then_200_returned(client: FlaskClient):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "xss"})
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert response.status_code == 200


def test__refresh__given_refresh_token__then_new_token_returned(client: FlaskClient):
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert "access_token" in response.json
    assert response.status_code == 200


def test__logout__given_jti__then_added_to_blocklist(client: FlaskClient):
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"})
    assert db.session.query(Blocklist).count() == 1
    assert response.json == {"msg": "Logged out successfully"}
    assert response.status_code == 200
