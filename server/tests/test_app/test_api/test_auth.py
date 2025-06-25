from unittest import mock

from app import db
from app.schemas import BlockedJti, User
from flask.testing import FlaskClient
from tests.helpers import Helpers


def test__login__given_credentials__when_already_authenticated__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/auth/login", json={"username": "test", "password": "test"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Already logged in"}
    assert response.status_code == 400


def test__login__given_credentials__when_password_is_wrong__then_403_returned(client_tester: FlaskClient):
    response = client_tester.post("/api/auth/login", json={"username": "admin", "password": "bad"})
    assert response.json == {"msg": "Bad username or password"}
    assert response.status_code == 403


def test__login__given_credentials__when_credentials_are_valid__then_200_returned(client_tester: FlaskClient):
    response = client_tester.post("/api/auth/login", json={"username": "admin", "password": "xss"})
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert response.status_code == 200


def test__login__given_credentials__when_mfa_configured__then_200_returned(client_tester: FlaskClient):
    user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
    user.mfa_secret = "ABC123"
    db.session.commit()
    response = client_tester.post("/api/auth/login", json={"username": "admin", "password": "xss"})
    assert response.json == {"msg": "OTP is required"}
    assert response.status_code == 200


@mock.patch("app.api.auth.pyotp")
def test__login__given_credentials__when_invalid_mfa__then_400_returned(pyotp_mocker: mock.MagicMock, client_tester: FlaskClient):
    pyotp_mocker.TOTP.return_value.verify.return_value = False

    user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
    user.mfa_secret = "ABC123"
    db.session.commit()
    response = client_tester.post("/api/auth/login", json={"username": "admin", "password": "xss", "otp": "123123"})
    assert response.json == {"msg": "Bad OTP"}
    assert response.status_code == 400


def test__refresh__given_refresh_token__then_new_token_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert "access_token" in response.json
    assert response.status_code == 200


def test__logout__given_jti__then_added_to_blocklist(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"})
    assert db.session.execute(db.select(db.func.count()).select_from(BlockedJti)).scalar() == 1
    assert response.json == {"msg": "Logged out successfully"}
    assert response.status_code == 200
