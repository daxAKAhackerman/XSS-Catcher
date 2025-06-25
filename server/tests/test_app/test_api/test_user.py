from unittest import mock

from app import db
from app.schemas import ApiKey, User
from flask.testing import FlaskClient
from tests.helpers import Helpers


def test__register__given_username__when_username_already_taken__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user", json={"username": "admin"}, headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 1
    assert response.json == {"msg": "This user already exists"}
    assert response.status_code == 400


@mock.patch("app.api.user.User.generate_password", return_value="random_password")
def test__register__given_username__then_user_created(generate_password_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user", json={"username": "dax"}, headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.execute(db.select(User).filter_by(username="dax")).scalar_one() is not None
    assert response.json == {"password": "random_password"}
    assert response.status_code == 200


@mock.patch("app.api.user.User.set_password")
def test__change_password__given_password__when_password_is_wrong__then_400_returned(set_password_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password123", "password2": "Password123", "old_password": "abc"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    set_password_mocker.assert_not_called()
    assert response.json == {"msg": "Old password is incorrect"}
    assert response.status_code == 400


def test__change_password__given_password__then_password_changed(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password123", "password2": "Password123", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user: User = db.session.execute(db.select(User).filter_by(username="admin")).scalar_one()
    assert user.check_password("Password123")
    assert response.json == {"msg": "Password changed successfully"}
    assert response.status_code == 200


def test__change_password__given_password__when_no_number__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password", "password2": "Password", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


def test__change_password__given_password__when_no_lower_case__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "PASSWORD123", "password2": "PASSWORD123", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


def test__change_password__given_password__when_no_upper_case__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "password123", "password2": "password123", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


def test__change_password__given_password__when_passwords_dont_match__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/user/password",
        json={"password1": "Password123", "password2": "Password1234", "old_password": "xss"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400


@mock.patch("app.api.user.User.generate_password", return_value="random_password")
def test__reset_password__given_user_id__then_password_is_reset(generate_password_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user/1/password", headers={"Authorization": f"Bearer {access_token}"})
    user: User = db.session.execute(db.select(User).filter_by(username="admin")).scalar_one()
    assert user.check_password("random_password")
    assert response.json == {"password": "random_password"}
    assert response.status_code == 200


def test__user_get__given_request__user_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.get("/api/user/current", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"first_login": True, "id": 1, "is_admin": True, "mfa": False, "username": "admin"}
    assert response.status_code == 200


def test__user_delete__given_user_id__when_only_one_user__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.delete("/api/user/1", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 1
    assert response.json == {"msg": "Can't delete the only user"}
    assert response.status_code == 400


def test__user_delete__given_user_id__when_deleting_yourself__then_400_returned(client_tester: FlaskClient):
    Helpers.create_user("dax")
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.delete("/api/user/1", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 2
    assert response.json == {"msg": "Can't delete yourself"}
    assert response.status_code == 400


def test__user_delete__given_user_id__then_user_deleted(client_tester: FlaskClient):
    user: User = Helpers.create_user("dax")
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.delete(f"/api/user/{user.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.execute(db.select(User).filter_by(id=user.id)).scalar_one_or_none() is None
    assert response.json == {"msg": f"User {user.username} deleted successfully"}
    assert response.status_code == 200


def test__user_patch__given_request__when_trying_to_demote_yourself__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.patch("/api/user/1", json={"is_admin": False}, headers={"Authorization": f"Bearer {access_token}"})
    user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
    assert user.is_admin is True
    assert response.json == {"msg": "Can't demote yourself"}
    assert response.status_code == 400


def test__user_patch__given_valid_request__then_user_privileges_changed(client_tester: FlaskClient):
    user: User = Helpers.create_user("dax")
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.patch(f"/api/user/{user.id}", json={"is_admin": True}, headers={"Authorization": f"Bearer {access_token}"})
    assert user.is_admin is True
    assert response.json == {"msg": f"User {user.username} modified successfully"}
    assert response.status_code == 200


def test__client_get_all__given_request__then_users_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.get("/api/user", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == [{"first_login": True, "id": 1, "is_admin": True, "mfa": False, "username": "admin"}]
    assert response.status_code == 200


@mock.patch("app.api.user.pyotp.random_base32", return_value="ABCD")
def test__get_mfa__given_request__then_mfa_info_returned(random_base32_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.get("/api/user/mfa", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {
        "qr_code": "iVBORw0KGgoAAAANSUhEUgAAAKsAAACrAQAAAAAxk1G0AAACwElEQVR4nOWXP86cMBDFB7lwBxew5Gu485WWCyxwAbiSO1/Dki+AOxcWk+csyZciRQalStBqYX9I43/z3swS/+5K9H/jk2gJNIe8ejMEWwINcly4zYFGr3Znj9CGCCLHwcyR3hpv6KXzFml+iO3p2xzTi/h4jEOaIpHOJTI/w9xeRBObJRg8LF+LF2Ds9xzN1+frGAQY1+XsFnB0efdt+EoICY5pwEKrIY1B2tthsmJ8kuKQOdhdI4MUxmE5vjyiqtVjkFyYd7LlAXb2cmmq6qg4fwRWhxyXakayJzXyaotm9GaRY0YCarUxUri9fT6YNzk+HfXYjrsuK5gZ5LhECzASDVgo253u1BRhZrCM2DtiR0PeDA9wQPg010TalsorfSQlxWmBLmsbkcWx7/0mx5fLq2ujSy+dXn12iuUYBvP2NIRuMxDEFD+xZbiw2rGySi+X975haZbji4hcGhg3u3sk460GEe73wJdu2LClYnZqk+PumozcQSloCx7inYMifHU9GbjLEhoWWvgjKRmGa8IhoEj49+XwQ7EcM1uufOrMDFF+LwUPcLdtdQR7VOSRXfUdW4RLzUdQJyX47ujUqvmQYxSxUcOoeEVG41ub+QEOUDak0OD9E2wmZpZjTG3USGELYRH6BbyU4wueXW2JZqltqvnyH9cUYkrk7VZVT+Fq+dalDPcDx3Gh1FfVy0j4UXRl2PR2o5sNwSqmoIocn1gWFMnd7eaqSk2DHF8+vZ2ZehLli2A5uTzAvSJ9DOZ7PYn3oYnwqdvLq9UlotQf7iIgw7jOXkPgVa3Hvr1KhnsXVtUFEQR79QneQ4pw75Fr97mlF4GflUSIA4DFrlPfaazSlmc4JKTPFtPYJXV3M1KMRhvdU6l9uav+tf/+Y8wojGrX6DVQG+3uMssx9vvdCzVCKpzeSmaW47/yz+ufwt8AD6YRyAq+9OUAAAAASUVORK5CYII=",
        "secret": "ABCD",
    }
    assert response.status_code == 200


@mock.patch("app.api.user.pyotp")
def test__set_mfa__given_otp__when_bad_otp__then_400_returned(pyotp_mocker: mock.MagicMock, client_tester: FlaskClient):
    pyotp_mocker.TOTP.return_value.verify.return_value = False

    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user/mfa", json={"secret": "A" * 32, "otp": "123123"}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {"msg": "Bad OTP"}
    assert response.status_code == 400


@mock.patch("app.api.user.pyotp")
def test__set_mfa__given_otp__when_good_otp__then_200_returned(pyotp_mocker: mock.MagicMock, client_tester: FlaskClient):
    pyotp_mocker.TOTP.return_value.verify.return_value = True

    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user/mfa", json={"secret": "A" * 32, "otp": "123123"}, headers={"Authorization": f"Bearer {access_token}"})

    user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
    assert user.mfa_secret == "A" * 32
    assert response.json == {"msg": "MFA set successfully"}
    assert response.status_code == 200


def test__delete_mfa__given_user_id__then_200_returned(client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")

    user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
    user.mfa_secret = "A" * 32
    db.session.commit()

    response = client_tester.delete(f"/api/user/{user.id}/mfa", headers={"Authorization": f"Bearer {access_token}"})
    assert user.mfa_secret is None
    assert response.json == {"msg": f"MFA removed for user {user.username}"}
    assert response.status_code == 200


@mock.patch("app.api.user.ApiKey.generate_key", return_value="11111111-1111-4111-a111-111111111111")
def test__create_api_key__given_request__then_api_key_created(generate_key_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user/apikey", headers={"Authorization": f"Bearer {access_token}"})

    assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 1
    assert response.json == {"id": 1, "key": "11111111-1111-4111-a111-111111111111"}


def test__create_api_key__given_request__when_already_5_api_keys__then_400_returned(client_tester: FlaskClient):
    for i in range(0, 5):
        Helpers.create_api_key()

    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user/apikey", headers={"Authorization": f"Bearer {access_token}"})

    assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 5
    assert response.json == {"msg": "You already have 5 API keys"}


def test__delete_api_key__given_key_id__then_key_deleted(client_tester: FlaskClient):
    api_key: ApiKey = Helpers.create_api_key()

    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.delete(f"/api/user/apikey/{api_key.id}", headers={"Authorization": f"Bearer {access_token}"})

    assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 0
    assert response.json == {"msg": "API key deleted successfully"}


def test__list_api_keys__given_user_id__then_key_list_returned(client_tester: FlaskClient):
    Helpers.create_api_key(key="11111111-1111-4111-a111-111111111111")

    access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
    response = client_tester.get("/api/user/1/apikey", headers={"Authorization": f"Bearer {access_token}"})

    assert [{"id": 1, "key": "********************************1111"}]
