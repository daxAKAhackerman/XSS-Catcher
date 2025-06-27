from app import db
from app.schemas import Client
from flask.testing import FlaskClient
from tests.helpers import Helpers


class TestCreateClient:
    def test__given_client_info__when_client_already_exists__then_400_returned(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/client", json={"name": client.name, "description": ""}, headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(Client)).scalar() == 1
        assert response.json == {"msg": "Client already exists"}
        assert response.status_code == 400

    def test__given_client_info__when_info_is_valid__then_201_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/client", json={"name": "test", "description": "hello world"}, headers={"Authorization": f"Bearer {access_token}"})
        client: Client = db.session.execute(db.select(Client)).scalar_one()
        assert client.name == "test"
        assert client.description == "hello world"
        assert response.json == {"msg": "New client test created successfully"}
        assert response.status_code == 201


class TestGetClient:
    def test__given_client_id__then_client_returned(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
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


class TestEditClient:
    def test__given_all_fields__when_fields_are_valid__then_client_edited(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        user = Helpers.create_user("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
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
        assert response.json == {"msg": "Client test2 edited successfully"}
        assert response.status_code == 200

    def test__given_name__when_name_already_exists__then_400_returned(self, client_tester: FlaskClient):
        client1 = Helpers.create_client("test")
        client2 = Helpers.create_client("test2")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch(f"/api/client/{client1.id}", json={"name": client2.name}, headers={"Authorization": f"Bearer {access_token}"})
        assert client1.name == "test"
        assert response.json == {"msg": "Another client already uses this name"}
        assert response.status_code == 400

    def test__given_owner__when_owner_does_not_exist__then_400_returned(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch(f"/api/client/{client.id}", json={"owner": 2}, headers={"Authorization": f"Bearer {access_token}"})
        assert client.owner_id == 1
        assert response.json == {"msg": "This user does not exist"}
        assert response.status_code == 400

    def test__given_request__when_unsettable_fields_absent__then_fields_kept(self, client_tester: FlaskClient):
        client = Helpers.create_client(name="test", description="hello world", webhook_url="some-url", mail_to="some-email")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        client_tester.patch(f"/api/client/{client.id}", json={}, headers={"Authorization": f"Bearer {access_token}"})
        assert client.mail_to == "some-email"
        assert client.description == "hello world"
        assert client.mail_to == "some-email"

    def test__given_request__when_unsettable_fields_set_to_none__then_fields_removed(self, client_tester: FlaskClient):
        client = Helpers.create_client(name="test", description="hello world", webhook_url="some-url", mail_to="some-email")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        client_tester.patch(
            f"/api/client/{client.id}", json={"mail_to": None, "webhook_url": None, "description": None}, headers={"Authorization": f"Bearer {access_token}"}
        )
        assert client.mail_to is None
        assert client.description is None
        assert client.mail_to is None


class TestDeleteClient:
    def test__given_client_id__then_client_deleted(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete(f"/api/client/{client.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(Client)).scalar() == 0
        assert response.json == {"msg": "Client test deleted successfully"}
        assert response.status_code == 200


class TestGetAllClients:
    def test__given_request__then_clients_returned(self, client_tester: FlaskClient):
        client = Helpers.create_client("test")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/client", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == [{"data": 0, "id": client.id, "name": client.name, "owner_id": client.owner_id, "reflected": 0, "stored": 0}]
        assert response.status_code == 200
