from unittest import mock

import jwt
from fastapi.testclient import TestClient
from tests.integration.conftest import (
    create_blocked_jti,
    create_user,
    delete_user,
    login,
)


class TestLogin:
    def test__when_login_with_valid_credentials__then_tokens_returned(self, test_client: TestClient):
        create_user()

        response = test_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test__when_login_with_invalid_credentials__then_401_returned(self, test_client: TestClient):
        response = test_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
        assert response.status_code == 401

    def test__when_user_with_mfa_but_not_provided__then_401_returned(self, test_client: TestClient):
        create_user(mfa_secret="abc123")

        response = test_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
        assert response.status_code == 401

    @mock.patch("endpoints.auth.pyotp.TOTP")
    def test__when_user_with_valid_mfa__then_tokens_returned(self, TotpMocker: mock.MagicMock, test_client: TestClient):
        TotpMocker.return_value.verify.return_value = True
        create_user(mfa_secret="abc123")

        response = test_client.post("/api/auth/login", json={"username": "admin", "password": "admin", "otp": "123456"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    @mock.patch("endpoints.auth.pyotp.TOTP")
    def test__when_user_with_invalid_mfa__then_401_returned(self, TotpMocker: mock.MagicMock, test_client: TestClient):
        TotpMocker.return_value.verify.return_value = False
        create_user(mfa_secret="abc123")

        response = test_client.post("/api/auth/login", json={"username": "admin", "password": "admin", "otp": "123456"})
        assert response.status_code == 401


class TestRefreshToken:
    def test__when_refresh_token_valid__then_access_token_returned(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test__when_refresh_token_valid_but_user_does_not_exist__then_401_returned(self, test_client: TestClient):
        user = create_user()
        access_token, refresh_token, bearear_auth = login(test_client)
        delete_user(user)

        response = test_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401


class TestLogout:
    def test__when_logout__then_cannot_use_token_anymore(self, test_client: TestClient):
        create_user()
        access_token, refresh_token, bearear_auth = login(test_client)

        response = test_client.post("/api/auth/logout", auth=bearear_auth)
        assert response.status_code == 200
        assert test_client.get("/api/user/current", auth=bearear_auth).status_code == 401
        assert test_client.post("/api/auth/refresh", json={"refresh_token": refresh_token}).status_code == 401
