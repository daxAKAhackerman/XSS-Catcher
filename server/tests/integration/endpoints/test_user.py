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
