from app import db
from app.models import Client
from flask.testing import FlaskClient
from tests.helpers import create_client, create_user, login


def test__client_post__given_client_info__when_client_already_exists__then_400_returned(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/client", json={"name": client.name, "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Client already exists"}
    assert response.status_code == 400


def test__client_post__given_client_info__when_info_is_valid__then_201_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/client", json={"name": "test", "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
    client: Client = db.session.query(Client).first()
    assert client.name == "test"
    assert client.description == ""
    assert response.json == {"msg": "New client test created successfuly"}
    assert response.status_code == 201


def test__client_get__given_client_id__then_client_returned(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get(f"/api/client/{client.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {
        "description": client.description,
        "id": client.id,
        "mail_to": client.mail_to,
        "name": client.name,
        "owner": "admin",
        "webhook_url": client.webhook_url,
    }
    assert response.status_code == 200


def test__client_patch__given_all_fields__when_fields_are_valid__then_client_edited(client_tester: FlaskClient):
    client = create_client("test")
    user = create_user("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(
        f"/api/client/{client.id}",
        json={"name": "test2", "description": "hello world", "owner": user.id, "mail_to": "user@example.com", "webhook_url": "https://example.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert client.name == "test2"
    assert client.description == "hello world"
    assert client.owner_id == 2
    assert client.mail_to == "user@example.com"
    assert client.webhook_url == "https://example.com"
    assert response.json == {"msg": "Client test2 edited successfuly"}
    assert response.status_code == 200


def test__client_patch__given_name__when_name_already_exists__then_400_returned(client_tester: FlaskClient):
    client1 = create_client("test")
    client2 = create_client("test2")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(f"/api/client/{client1.id}", json={"name": client2.name}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Another client already uses this name"}
    assert response.status_code == 400


def test__client_patch__given_owner__when_owner_does_not_exist__then_400_returned(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(f"/api/client/{client.id}", json={"owner": 2}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "This user does not exist"}
    assert response.status_code == 400


def test__client_patch__given_mail_to__when_empty_string__then_field_set_to_none(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    client_tester.patch(f"/api/client/{client.id}", json={"mail_to": "user@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    client_tester.patch(f"/api/client/{client.id}", json={"mail_to": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert client.mail_to is None


def test__client_patch__given_webhook_url__when_empty_string__then_field_set_to_none(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    client_tester.patch(f"/api/client/{client.id}", json={"webhook_url": "https://example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    client_tester.patch(f"/api/client/{client.id}", json={"webhook_url": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert client.webhook_url is None


def test__client_delete__given_client_id__then_client_deleted(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.delete(f"/api/client/{client.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(Client).count() == 0
    assert response.json == {"msg": "Client test deleted successfuly"}
    assert response.status_code == 200


def test__client_get_all__given_request__then_clients_returned(client_tester: FlaskClient):
    client = create_client("test")
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get("/api/client", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [{"data": 0, "id": client.id, "name": client.name, "owner_id": client.owner_id, "reflected": 0, "stored": 0}]
    assert response.status_code == 200
