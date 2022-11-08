from app import db
from app.models import Client
from flask.testing import FlaskClient
from tests.helpers import create_client, create_user, login


def test__client_post__given_client_info__when_client_already_exists__then_400_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/client", json={"name": "test", "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Client already exists"}
    assert response.status_code == 400


def test__client_post__given_client_info__when_info_is_valid__then_201_returned(client: FlaskClient):
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.post("/api/client", json={"name": "test", "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    test_client: Client = db.session.query(Client).first()
    assert test_client.name == "test"
    assert test_client.description == ""
    assert response.json == {"msg": "New client test created successfuly"}
    assert response.status_code == 201


def test__client_get__given_client_id__then_client_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.get("/api/client/1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"description": "", "id": 1, "mail_to": None, "name": "test", "owner": "admin", "webhook_url": None}
    assert response.status_code == 200


def test__client_patch__given_all_fields__when_fields_are_valid__then_client_edited(client: FlaskClient):
    create_client("test")
    create_user("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.patch(
        "/api/client/1",
        json={"name": "test2", "description": "hello world", "owner": 2, "mail_to": "user@example.com", "webhook_url": "https://example.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    test_client: Client = db.session.query(Client).first()
    assert test_client.name == "test2"
    assert test_client.description == "hello world"
    assert test_client.owner_id == 2
    assert test_client.mail_to == "user@example.com"
    assert test_client.webhook_url == "https://example.com"
    assert response.json == {"msg": "Client test2 edited successfuly"}
    assert response.status_code == 200


def test__client_patch__given_name__when_name_already_exists__then_400_returned(client: FlaskClient):
    create_client("test")
    create_client("test2")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.patch("/api/client/1", json={"name": "test2"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Another client already uses this name"}
    assert response.status_code == 400


def test__client_patch__given_owner__when_owner_does_not_exist__then_400_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.patch("/api/client/1", json={"owner": 2}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "This user does not exist"}
    assert response.status_code == 400


def test__client_patch__given_mail_to__when_empty_string__then_field_set_to_none(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    client.patch("/api/client/1", json={"mail_to": "user@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    client.patch("/api/client/1", json={"mail_to": ""}, headers={"Authorization": f"Bearer {access_token}"})
    test_client: Client = db.session.query(Client).first()
    assert test_client.mail_to is None


def test__client_patch__given_webhook_url__when_empty_string__then_field_set_to_none(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    client.patch("/api/client/1", json={"webhook_url": "https://example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    client.patch("/api/client/1", json={"webhook_url": ""}, headers={"Authorization": f"Bearer {access_token}"})
    test_client: Client = db.session.query(Client).first()
    assert test_client.webhook_url is None


def test__client_delete__given_client_id__then_client_deleted(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.delete("/api/client/1", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(Client).count() == 0
    assert response.json == {"msg": "Client test deleted successfuly"}
    assert response.status_code == 200


def test__client_get_all__given_request__then_clients_returned(client: FlaskClient):
    create_client("test")
    access_token, refresh_token = login(client, "admin", "xss")
    response = client.get("/api/client", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [{"data": 0, "id": 1, "name": "test", "owner_id": 1, "reflected": 0, "stored": 0}]
    assert response.status_code == 200
