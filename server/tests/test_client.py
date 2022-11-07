from app import db
from app.models import Client
from flask.testing import FlaskClient
from tests.helpers import create_client, login


def test__client_post__given_client_info__when_client_already_exists__then_400_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/client", json={"name": "test", "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Client already exists"}
    assert response.status_code == 400


def test__client_post__given_client_info__when_info_is_valid__then_201_returned(client: FlaskClient):
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/client", json={"name": "test", "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(Client).count() == 1
    assert response.json == {"msg": "New client test created successfuly"}
    assert response.status_code == 201


def test__client_get__given_client_id__then_client_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.get("/api/client/1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"description": "", "id": 1, "mail_to": None, "name": "test", "owner": "admin", "webhook_url": None}
    assert response.status_code == 200
