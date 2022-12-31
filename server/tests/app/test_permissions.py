from unittest import mock

import pytest
from app import db
from app.models import ApiKey, Client, User
from app.permissions import (
    UserLookupError,
    _get_api_key_from_request,
    _get_user_from_api_key,
    _is_valid_uuid4,
    _verify_api_key_in_request,
    get_current_user,
)
from flask import g
from flask.testing import FlaskClient
from tests.helpers import create_api_key, create_client, create_user, login


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


def test__permissions__given_api_key__then_successfull_api_call(client_tester: FlaskClient):
    api_key: ApiKey = create_api_key()

    response = client_tester.get(f"/api/user/current", headers={"Authorization": f"Bearer {api_key.key}"})

    assert response.json == {"first_login": True, "id": 1, "is_admin": True, "mfa": False, "username": "admin"}


@mock.patch("app.permissions._get_api_key_from_request")
@mock.patch("app.permissions._get_user_from_api_key")
def test___verify_api_key_in_request__when_api_key_present__return_true(
    _get_user_from_api_key_mocker: mock.MagicMock, _get_api_key_from_request_mocker: mock.MagicMock, client_tester: FlaskClient
):
    ret = _verify_api_key_in_request()

    _get_user_from_api_key_mocker.assert_called_once_with(api_key=_get_api_key_from_request_mocker.return_value)
    assert g._apikey_user == {"loaded_user": _get_user_from_api_key_mocker.return_value}
    assert ret is True


@mock.patch("app.permissions._get_api_key_from_request", return_value=False)
def test___verify_api_key_in_request__when_api_key_present__return_false(_get_api_key_from_request_mocker: mock.MagicMock, client_tester: FlaskClient):
    ret = _verify_api_key_in_request()

    assert g.get("_apikey_user") is None
    assert ret is False


def test___get_api_key_from_request__when_no_authorization_header__return_none(client_tester: FlaskClient):
    with client_tester.application.test_request_context() as request_context:
        request_context.request.headers = {}
        assert _get_api_key_from_request() is None


def test___get_api_key_from_request__when_value_is_not_uuid__return_none(client_tester: FlaskClient):
    with client_tester.application.test_request_context() as request_context:
        request_context.request.headers = {"Authorization": "Bearer ABC"}
        assert _get_api_key_from_request() is None


def test___get_api_key_from_request__when_valid_api_key__return_none(client_tester: FlaskClient):
    api_key: ApiKey = create_api_key()

    with client_tester.application.test_request_context() as request_context:
        request_context.request.headers = {"Authorization": f"Bearer {api_key.key}"}
        assert _get_api_key_from_request() is api_key


def test___get_user_from_api_key__given_api_key__when_user_exists__then_user_returned(client_tester: FlaskClient):
    api_key: ApiKey = create_api_key()
    user: User = db.session.query(User).filter_by(id=1).one()

    assert _get_user_from_api_key(api_key) is user


def test___get_user_from_api_key__given_api_key__when_user_does_not_exist__then_raise(client_tester: FlaskClient):
    api_key: ApiKey = create_api_key(user_id=2)
    with pytest.raises(UserLookupError):
        _get_user_from_api_key(api_key)


def test___is_valid_uuid4__given_valid_uuid__then_return_true():
    assert _is_valid_uuid4("11111111-1111-4111-a111-111111111111") is True


def test___is_valid_uuid4__given_invalid_uuid__then_return_false():
    assert _is_valid_uuid4("ABC") is False


def test__get_current_user__when_api_key__then_api_key_owner_returned(client_tester: FlaskClient):
    user: User = db.session.query(User).filter_by(id=1).one()
    g._apikey_user = {"loaded_user": user}
    assert get_current_user() is user


@mock.patch("app.permissions.flask_jwt_extended.get_current_user")
def test__get_current_user__when_no_api_key__then_jwt_function_called(get_current_user_mocker: mock.MagicMock, client_tester: FlaskClient):
    assert get_current_user() is get_current_user_mocker.return_value
