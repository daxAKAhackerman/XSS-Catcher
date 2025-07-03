from typing import Callable, cast
from unittest import mock

import pytest
from app import db
from app.permissions import (
    InvalidApiKeyException,
    Permission,
    _get_api_key_header,
    _is_valid_uuid4,
    _validate_api_key,
    authorization_required,
    get_current_user,
    permissions,
)
from app.schemas import ApiKey, User
from flask import g
from flask.testing import FlaskClient
from tests.helpers import Helpers
from werkzeug.datastructures import Headers


class TestAuthorizationRequired:
    @pytest.fixture()
    def test_fn(self, request: pytest.FixtureRequest) -> Callable:
        parametrization = {}
        if hasattr(request, "param"):
            parametrization = request.param

        @authorization_required(**parametrization)
        def _test_fn() -> tuple[dict[str, str], int]:
            return ({"msg": "OK"}, 200)

        return _test_fn

    def test__when_valid_api_key__then_function_called(self, test_fn: Callable, client_tester: FlaskClient):
        api_key: ApiKey = Helpers.create_api_key()
        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {api_key.key}"})
            ret = test_fn()
            assert ret[1] == 200
            assert g.get("_api_key_user") == {"loaded_user": user}

    def test__when_invalid_api_key__then_error_returned(self, test_fn: Callable, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": "Bearer 11111111-1111-4111-a111-111111111111"})
            ret = test_fn()
            assert ret[1] == 401

    @pytest.mark.parametrize("test_fn", [{"optional": True}], indirect=True)
    def test__when_invalid_api_key_and_optional__then_function_called(self, test_fn: Callable, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": "Bearer 11111111-1111-4111-a111-111111111111"})
            ret = test_fn()
            assert ret[1] == 200

    @pytest.mark.parametrize("test_fn", [{"refresh": True}], indirect=True)
    def test__valid_api_key_and_refresh__the_error_returned(self, test_fn: Callable, client_tester: FlaskClient):
        api_key: ApiKey = Helpers.create_api_key()
        db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {api_key.key}"})
            ret = test_fn()
            assert ret[1] == 422

    def test__when_valid_jwt__then_function_called(self, test_fn: Callable, client_tester: FlaskClient):
        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            ret = test_fn()
            assert ret[1] == 200
            assert g.get("_jwt_extended_jwt_user") == {"loaded_user": user}


class TestPermissions:
    @pytest.fixture()
    def test_fn(self, request: pytest.FixtureRequest) -> Callable:
        parametrization = {}
        if hasattr(request, "param"):
            parametrization = request.param

        @authorization_required()
        @permissions(**parametrization)
        def _test_fn(*args, **kwargs):
            pass

        return _test_fn

    @pytest.mark.parametrize("test_fn", [{"all_of": {Permission.OWNER}}], indirect=True)
    def test__when_user_id_in_request__then_owner_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(user_id=1) is None
            assert test_fn(user_id=2) == ({"msg": "Forbidden"}, 403)

    @pytest.mark.parametrize("test_fn", [{"all_of": {Permission.OWNER}}], indirect=True)
    def test__when_client_id_in_request__then_owner_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        Helpers.create_user("user2")
        Helpers.create_client("test")
        Helpers.create_client("test2", owner_id=2)
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(client_id=1) is None
            assert test_fn(client_id=2) == ({"msg": "Forbidden"}, 403)

    @pytest.mark.parametrize("test_fn", [{"all_of": {Permission.OWNER}}], indirect=True)
    def test__when_xss_id_in_request__then_owner_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        Helpers.create_user("user2")
        Helpers.create_client("test")
        Helpers.create_client("test2", owner_id=2)
        Helpers.create_xss()
        Helpers.create_xss(client_id=2)

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(xss_id=1) is None
            assert test_fn(xss_id=2) == ({"msg": "Forbidden"}, 403)

    @pytest.mark.parametrize("test_fn", [{"all_of": {Permission.OWNER}}], indirect=True)
    def test__when_key_id_in_request__then_owner_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        Helpers.create_user("user2")
        Helpers.create_api_key()
        Helpers.create_api_key(user_id=2)

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(key_id=1) is None
            assert test_fn(key_id=2) == ({"msg": "Forbidden"}, 403)

    @pytest.mark.parametrize("test_fn", [{"all_of": {Permission.OWNER, Permission.ADMIN}}], indirect=True)
    def test__when_all_of_used__then_all_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(user_id=1) is None
            assert test_fn(user_id=2) == ({"msg": "Forbidden"}, 403)

    @pytest.mark.parametrize("test_fn", [{"any_of": {Permission.OWNER, Permission.ADMIN}}], indirect=True)
    def test__when_any_of_used__then_one_permission_enforced(self, test_fn: Callable, client_tester: FlaskClient):
        Helpers.create_user("test")

        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        test_access_token, test_refresh_token = Helpers.login(client_tester, "test", "test")
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {access_token}"})
            assert test_fn(user_id=2) is None
            request_context.request.headers = Headers({"Authorization": f"Bearer {test_access_token}"})
            assert test_fn(user_id=1) == ({"msg": "Forbidden"}, 403)


class TestGetApiKeyHeader:
    def test__when_no_authorization_header__return_none(self, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers()
            assert _get_api_key_header() is None

    def test__when_value_is_not_uuid__return_none(self, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": "Bearer ABC"})
            assert _get_api_key_header() is None

    def test__when_value_is_valid_api_key__then_key_returned(self, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": "Bearer 11111111-1111-4111-a111-111111111111"})
            assert _get_api_key_header() == "11111111-1111-4111-a111-111111111111"


class TestIsValidUuid4:
    def test__given_valid_uuid__then_return_true(self):
        assert _is_valid_uuid4("11111111-1111-4111-a111-111111111111") is True

    def test__given_invalid_uuid__then_return_false(self):
        assert _is_valid_uuid4("ABC") is False


class TestValidateApiKey:
    def test___when_valid_api_key__return_none(self, client_tester: FlaskClient):
        api_key: ApiKey = Helpers.create_api_key()
        owner: User = cast(User, api_key.owner)  # type:ignore

        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": f"Bearer {api_key.key}"})
            assert _validate_api_key(api_key.key) is None
            assert g._api_key_user == {"loaded_user": owner}

    def test__when_invalid_api_key__raise(self, client_tester: FlaskClient):
        with client_tester.application.test_request_context() as request_context:
            request_context.request.headers = Headers({"Authorization": "Bearer 11111111-1111-4111-a111-111111111111"})
            with pytest.raises(InvalidApiKeyException):
                _validate_api_key("11111111-1111-4111-a111-111111111111")


class TestGetCurrentUser:
    def test__when_api_key__then_api_key_owner_returned(self, client_tester: FlaskClient):
        user: User = db.session.execute(db.select(User).filter_by(id=1)).scalar_one()
        g._api_key_user = {"loaded_user": user}
        assert get_current_user() is user

    @mock.patch("app.permissions.flask_jwt_extended.get_current_user")
    def test__when_jwt_header__then_jwt_function_called(self, get_current_user_mocker: mock.MagicMock, client_tester: FlaskClient):
        assert get_current_user() is get_current_user_mocker.return_value
