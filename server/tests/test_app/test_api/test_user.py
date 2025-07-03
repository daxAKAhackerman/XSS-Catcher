from unittest import mock

from app import db
from app.schemas import ApiKey, User
from flask.testing import FlaskClient
from tests.helpers import Helpers


class TestRegister:
    def test__given_username__when_username_already_taken__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user", json={"username": "admin"}, headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 1
        assert response.json == {"msg": "This user already exists"}
        assert response.status_code == 400

    @mock.patch("app.api.user.User.generate_password", return_value="random_password")
    def test__given_username__then_user_created(self, generate_password_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user", json={"username": "dax"}, headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(User).filter_by(username="dax")).scalar_one() is not None
        assert response.json == {"password": "random_password"}
        assert response.status_code == 200


class TestChangePassword:
    @mock.patch("app.api.user.User.set_password")
    def test__given_password__when_password_is_wrong__then_400_returned(self, set_password_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/user/password",
            json={"password1": "Password123", "password2": "Password123", "old_password": "abc"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        set_password_mocker.assert_not_called()
        assert response.json == {"msg": "Old password is incorrect"}
        assert response.status_code == 400

    def test__given_password__then_password_changed(self, client_tester: FlaskClient):
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

    def test__given_password__when_no_number__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/user/password",
            json={"password1": "Password", "password2": "Password", "old_password": "xss"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 400

    def test__given_password__when_no_lower_case__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/user/password",
            json={"password1": "PASSWORD123", "password2": "PASSWORD123", "old_password": "xss"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 400

    def test__given_password__when_no_upper_case__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/user/password",
            json={"password1": "password123", "password2": "password123", "old_password": "xss"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 400

    def test__given_password__when_passwords_dont_match__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/user/password",
            json={"password1": "Password123", "password2": "Password1234", "old_password": "xss"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 400


class TestResetPassword:
    @mock.patch("app.api.user.User.generate_password", return_value="random_password")
    def test__given_user_id__then_password_is_reset(self, generate_password_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user/1/password", headers={"Authorization": f"Bearer {access_token}"})
        user: User = db.session.execute(db.select(User).filter_by(username="admin")).scalar_one()
        assert user.check_password("random_password")
        assert response.json == {"password": "random_password"}
        assert response.status_code == 200


class TestGetUser:
    def test__given_request__user_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/user/current", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {"first_login": True, "id": 1, "is_admin": True, "mfa": False, "username": "admin"}
        assert response.status_code == 200


class TestDeleteUser:
    def test__given_user_id__when_only_one_user__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete("/api/user/1", headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 1
        assert response.json == {"msg": "Can't delete the only user"}
        assert response.status_code == 400

    def test__given_user_id__when_deleting_yourself__then_400_returned(self, client_tester: FlaskClient):
        Helpers.create_user("dax")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete("/api/user/1", headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(db.func.count()).select_from(User)).scalar() == 2
        assert response.json == {"msg": "Can't delete yourself"}
        assert response.status_code == 400

    def test__given_user_id__then_user_deleted(self, client_tester: FlaskClient):
        user: User = Helpers.create_user("dax")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete(f"/api/user/{user.id}", headers={"Authorization": f"Bearer {access_token}"})
        assert db.session.execute(db.select(User).filter_by(id=user.id)).scalar_one_or_none() is None
        assert response.json == {"msg": f"User {user.username} deleted successfully"}
        assert response.status_code == 200


class TestEditUser:
    def test__given_request__when_trying_to_demote_yourself__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch("/api/user/1", json={"is_admin": False}, headers={"Authorization": f"Bearer {access_token}"})
        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        assert user.is_admin is True
        assert response.json == {"msg": "Can't demote yourself"}
        assert response.status_code == 400

    def test__given_valid_request__then_user_privileges_changed(self, client_tester: FlaskClient):
        user: User = Helpers.create_user("dax")
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch(f"/api/user/{user.id}", json={"is_admin": True}, headers={"Authorization": f"Bearer {access_token}"})
        assert user.is_admin is True
        assert response.json == {"msg": f"User {user.username} modified successfully"}
        assert response.status_code == 200


class TestGetAllUsers:
    def test__given_request__then_users_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/user", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == [{"first_login": True, "id": 1, "is_admin": True, "mfa": False, "username": "admin"}]
        assert response.status_code == 200


class TestGetMfa:
    @mock.patch("app.api.user.pyotp.random_base32", return_value="ABCD")
    def test__given_request__then_mfa_info_returned(self, random_base32_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/user/mfa", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {
            "qr_code": "iVBORw0KGgoAAAANSUhEUgAAAKsAAACrAQMAAAAjJv5aAAAABlBMVEWc3P4fHx+yV3sdAAAAAnRSTlP//8i138cAAALASURBVHic5Zc/zpwwEMUHuXAHF7Dka7jzlZYLLHABuJI7X8OSL4A7FxaT5yzJlyJFBqVK0Gphf0jjf/PezBL/7kr0f+OTaAk0h7x6MwRbAg1yXLjNgUavdmeP0IYIIsfBzJHeGm/opfMWaX6I7enbHNOL+HiMQ5oikc4lMj/D3F5EE5slGDwsX4sXYOz3HM3X5+sYBBjX5ewWcHR59234SggJjmnAQqshjUHa22GyYnyS4pA52F0jgxTGYTm+PKKq1WOQXJh3suUBdvZyaarqqDh/BFaHHJdqRrInNfJqi2b0ZpFjRgJqtTFSuL19Ppg3OT4d9diOuy4rmBnkuEQLMBINWCjbne7UFGFmsIzYO2JHQ94MD3BA+DTXRNqWyit9JCXFaYEuaxuRxbHv/SbHl8ura6NLL51efXaK5RgG8/Y0hG4zEMQUP7FluLDasbJKL5f3vmFpluOLiFwaGDe7eyTjrQYR7vfAl27YsKVidmqT4+6ajNxBKWgLHuKdgyJ8dT0ZuMsSGhZa+CMpGYZrwiGgSPj35fBDsRwzW6586swMUX4vBQ9wt211BHtU5JFd9R1bhEvNR1AnJfju6NSq+ZBjFLFRw6h4RUbjW5v5AQ5QNqTQ4P0TbCZmlmNMbdRIYQthEfoFvJTjC55dbYlmqW2q+fIf1xRiSuTtVlVP4Wr51qUM9wPHcaHUV9XLSPhRdGXY9Hajmw3BKqagihyfWBYUyd3t5qpKTYMcXz69nZl6EuWLYDm5PMC9In0M5ns9ifehifCp28ur1SWi1B/uIiDDuM5eQ+BVrce+vUqGexdW1QURBHv1Cd5DinDvkWv3uaUXgZ+VRIgDgMWuU99prNKWZzgkpM8W09gldXczUoxGG91TqX25q/61//5jzCiMatfoNVAb7e4yyzH2+90LNUIqnN5KZpbjv/LP65/C3wAPphHICr705QAAAABJRU5ErkJggg==",
            "secret": "ABCD",
        }
        assert response.status_code == 200


class TestSetMfa:
    @mock.patch("app.api.user.pyotp")
    def test__given_otp__when_bad_otp__then_400_returned(self, pyotp_mocker: mock.MagicMock, client_tester: FlaskClient):
        pyotp_mocker.TOTP.return_value.verify.return_value = False

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user/mfa", json={"secret": "A" * 32, "otp": "123123"}, headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {"msg": "Bad OTP"}
        assert response.status_code == 400

    @mock.patch("app.api.user.pyotp")
    def test__given_otp__when_good_otp__then_200_returned(self, pyotp_mocker: mock.MagicMock, client_tester: FlaskClient):
        pyotp_mocker.TOTP.return_value.verify.return_value = True

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user/mfa", json={"secret": "A" * 32, "otp": "123123"}, headers={"Authorization": f"Bearer {access_token}"})

        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        assert user.mfa_secret == "A" * 32
        assert response.json == {"msg": "MFA set successfully"}
        assert response.status_code == 200


class TestDeleteMfa:
    def test__given_user_id__then_200_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")

        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        user.mfa_secret = "A" * 32
        db.session.commit()

        response = client_tester.delete(f"/api/user/{user.id}/mfa", headers={"Authorization": f"Bearer {access_token}"})
        assert user.mfa_secret is None
        assert response.json == {"msg": f"MFA removed for user {user.username}"}
        assert response.status_code == 200


class TestCreateApiKey:
    @mock.patch("app.api.user.ApiKey.generate_key", return_value="11111111-1111-4111-a111-111111111111")
    def test__given_request__then_api_key_created(self, generate_key_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user/apikey", headers={"Authorization": f"Bearer {access_token}"})

        assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 1
        assert response.json == {"id": 1, "key": "11111111-1111-4111-a111-111111111111"}

    def test__given_request__when_already_5_api_keys__then_400_returned(self, client_tester: FlaskClient):
        for i in range(0, 5):
            Helpers.create_api_key()

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/user/apikey", headers={"Authorization": f"Bearer {access_token}"})

        assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 5
        assert response.json == {"msg": "You already have 5 API keys"}


class TestDeleteApiKey:
    def test__given_key_id__then_key_deleted(self, client_tester: FlaskClient):
        api_key: ApiKey = Helpers.create_api_key()

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.delete(f"/api/user/apikey/{api_key.id}", headers={"Authorization": f"Bearer {access_token}"})

        assert db.session.execute(db.select(db.func.count()).select_from(ApiKey)).scalar() == 0
        assert response.json == {"msg": "API key deleted successfully"}


class TestListApiKeys:
    def test__given_user_id__then_key_list_returned(self, client_tester: FlaskClient):
        Helpers.create_api_key(key="11111111-1111-4111-a111-111111111111")

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/user/1/apikey", headers={"Authorization": f"Bearer {access_token}"})

        assert response.json == [{"id": 1, "key": "****************************11111111"}]
