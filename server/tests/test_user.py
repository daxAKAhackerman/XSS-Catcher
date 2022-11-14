from unittest import mock

from app import db
from app.models import User
from flask.testing import FlaskClient
from tests.helpers import login


def test__register__given_username__when_username_already_taken__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user", json={"username": "admin"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "This user already exists"}
    assert response.status_code == 400


@mock.patch("app.api.user.User.generate_password", return_value="random_password")
def test__register__given_username__then_user_created(generate_password_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user", json={"username": "dax"}, headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(User).filter_by(username="dax").first() is not None
    assert response.json == {"password": "random_password"}
    assert response.status_code == 200


@mock.patch("app.api.user.User.set_password")
def test__change_password__given_password__when_password_is_wrong__then_400_returned(set_password_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password123", "password2": "Password123", "old_password": "abc"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    set_password_mocker.assert_not_called()
    assert response.json == {"msg": "Old password is incorrect"}
    assert response.status_code == 400


def test__change_password__given_password__then_password_changed(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password123", "password2": "Password123", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user: User = db.session.query(User).filter_by(username="admin").first()
    assert user.check_password("Password123")
    assert response.json == {"msg": "Password changed successfuly"}
    assert response.status_code == 200
