from app.models import Client
from flask.testing import FlaskClient
from tests.helpers import create_client, create_user, login


def test__permissions__given_all_of_permission__when_unauthorized__then_403_returned(client_tester: FlaskClient):
    create_user(username="test")
    access_token, refresh_token = login(client_tester, "test", "test")
    response = client_tester.post("/api/user/1/password", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Forbidden"}
    assert response.status_code == 403


def test__permissions__given_one_of_permission__when_unauthorized__then_403_returned(client_tester: FlaskClient):
    create_user(username="test")
    client: Client = create_client("test")
    access_token, refresh_token = login(client_tester, "test", "test")
    response = client_tester.delete(f"/api/client/{client.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Forbidden"}
    assert response.status_code == 403
