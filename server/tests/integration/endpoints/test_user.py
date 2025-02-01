from typing import cast

from fastapi.testclient import TestClient
from tests.integration.helpers import create_user, login


class TestCreateUser:
    def test__when_request_valid__then_user_created_and_password_returned(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post("/api/user", json={"username": "dax"}, auth=bearear_auth)

        password = response.json()["password"]
        login(test_client, "dax", password)
        assert response.status_code == 200

    def test__when_user_already_exists__then_400_returned(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post("/api/user", json={"username": "admin"}, auth=bearear_auth)

        assert response.status_code == 400


class TestChangePassword:
    def test__when_old_password_correct__then_password_changed(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post("/api/user/password", json={"old_password": "admin", "password1": "Password1", "password2": "Password1"}, auth=bearear_auth)

        login(test_client, "admin", "Password1")
        assert response.status_code == 200

    def test__when_old_password_incorrect__then_400_returned(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post(
            "/api/user/password", json={"old_password": "incorrect", "password1": "Password1", "password2": "Password1"}, auth=bearear_auth
        )

        assert response.status_code == 400


class TestResetPassword:
    def test__when_user_exists__then_password_reset(self, test_client: TestClient):
        user = create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post(f"/api/user/{user.id}/password", auth=bearear_auth)

        login(test_client, "admin", response.json()["password"])
        assert response.status_code == 200

    def test__when_user_does_not_exist__then_404_returned(self, test_client: TestClient):
        user = create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post(f"/api/user/{cast(int, user.id) + 10}/password", auth=bearear_auth)

        assert response.status_code == 404
