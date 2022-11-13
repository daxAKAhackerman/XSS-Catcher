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
def test__register__given_username__then_user_created(generate_password: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/user", json={"username": "dax"}, headers={"Authorization": f"Bearer {access_token}"})
    assert db.session.query(User).filter_by(username="dax").first() is not None
    assert response.json == {"password": "random_password"}
    assert response.status_code == 200
