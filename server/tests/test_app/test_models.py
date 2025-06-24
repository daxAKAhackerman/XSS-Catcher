import re
import uuid
from unittest import mock

import pytest
from app import db
from app.schemas import (
    XSS,
    ApiKey,
    BlockedJti,
    Client,
    Settings,
    User,
    check_if_token_in_blocklist,
    init_app,
    user_loader_callback,
)
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import Helpers


class TestClient:
    def test__summary__given_self__then_summary_returned(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        Helpers.create_xss(data={"TestKey": "TestValue", "TestKey2": "TestValue2"})
        assert client.summary() == {"owner_id": 1, "id": 1, "name": "test", "reflected": 0, "stored": 1, "data": 2}

    def test__to_dict__given_self__then_dict_returned(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test", mail_to="test@example.com", webhook_url="http://127.0.0.1")
        assert client.to_dict() == {
            "owner": "admin",
            "id": 1,
            "name": "test",
            "description": "",
            "mail_to": "test@example.com",
            "webhook_url": "http://127.0.0.1",
        }

    def test__to_dict__given_self__when_owner_does_not_exist__then_dict_returned_with_nobody_owner(self, client_tester: FlaskClient):
        user = Helpers.create_user("test")
        client: Client = Helpers.create_client("test", mail_to="test@example.com", webhook_url="http://127.0.0.1", owner_id=2)
        db.session.delete(user)
        db.session.commit()
        assert client.to_dict() == {"owner": None, "id": 1, "name": "test", "description": "", "mail_to": "test@example.com", "webhook_url": "http://127.0.0.1"}

    def test__set_uid__given_self__then_uid_set(self, client_tester: FlaskClient):
        client = Client()
        client.set_uid()
        assert re.match(r"^[A-Za-z\d]{6}$", client.uid)

    @mock.patch("app.schemas.random.choice")
    def test__set_uid__given_self__when_uid_exists__then_new_uid_set(self, choice_mocker: mock.MagicMock, client_tester: FlaskClient):
        choice_mocker.side_effect = ["a", "a", "a", "a", "a", "a", "b", "b", "b", "b", "b", "b"]
        Helpers.create_client(name="test", uid="aaaaaa")
        client2 = Client()
        client2.set_uid()
        assert client2.uid == "bbbbbb"


class TestXSS:
    @freeze_time("2000-01-01")
    def test__summary__given_self__then_summary_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test")
        xss: XSS = Helpers.create_xss(tags=["tag1"])
        assert xss.summary() == {"id": 1, "ip_addr": "127.0.0.1", "timestamp": 946684800, "tags": ["tag1"]}

    @freeze_time("2000-01-01")
    def test__to_dict__given_self__then_dict_returned(self, client_tester: FlaskClient):
        Helpers.create_client("test")
        xss: XSS = Helpers.create_xss(tags=["tag1"], data={"TestKey": "TestValue"}, headers={"HeaderKey": "HeaderValue"})
        assert xss.to_dict() == {
            "id": 1,
            "headers": {"HeaderKey": "HeaderValue"},
            "ip_addr": "127.0.0.1",
            "data": {"TestKey": "TestValue"},
            "timestamp": 946684800,
            "tags": ["tag1"],
        }

    @freeze_time("2000-01-01")
    def test__to_dict__given_self__when_big_data__then_dict_returned_without_big_data(self, client_tester: FlaskClient):
        Helpers.create_client("test")
        xss: XSS = Helpers.create_xss(tags=["tag1"], data={"fingerprint": "abc", "dom": "abc", "screenshot": "abc"}, headers={"HeaderKey": "HeaderValue"})
        assert xss.to_dict() == {
            "id": 1,
            "headers": {"HeaderKey": "HeaderValue"},
            "ip_addr": "127.0.0.1",
            "data": {"fingerprint": "", "dom": "", "screenshot": ""},
            "timestamp": 946684800,
            "tags": ["tag1"],
        }


class TestApiKey:
    @mock.patch("app.schemas.uuid.uuid4", return_value=uuid.UUID("11111111-1111-4111-a111-111111111111", version=4))
    def test__generate_key__then_return_uuid(self, uuid4_mocker: mock.MagicMock, client_tester: FlaskClient):
        assert ApiKey.generate_key() == "11111111-1111-4111-a111-111111111111"

    def test__to_dict__given_self__then_dict_returned(self, client_tester: FlaskClient):
        api_key = Helpers.create_api_key(key="11111111-1111-4111-a111-111111111111")
        assert api_key.to_dict() == {"id": 1, "key": "11111111-1111-4111-a111-111111111111"}

    def test__to_obfuscated_dict__given_self__then_obfuscated_dict_returned(self, client_tester: FlaskClient):
        api_key = Helpers.create_api_key(key="11111111-1111-4111-a111-111111111111")
        assert api_key.to_obfuscated_dict() == {"id": 1, "key": "****************************11111111"}


class TestUser:
    @mock.patch("app.schemas.generate_password_hash")
    def test__set_password__given_password__then_password_changed(self, generate_password_hash_mocker: mock.MagicMock, client_tester: FlaskClient):
        user = User()
        user.set_password("test")
        generate_password_hash_mocker.assert_called_once_with("test")
        assert user.password_hash is generate_password_hash_mocker.return_value

    @mock.patch("app.schemas.check_password_hash")
    def test__check_password__given_password__then_password_checked(self, check_password_hash_mocker: mock.MagicMock, client_tester: FlaskClient):
        user: User = Helpers.create_user("test")
        password_check = user.check_password("test")
        check_password_hash_mocker.assert_called_once_with(user.password_hash, "test")
        assert password_check is check_password_hash_mocker.return_value

    def test__generate_password__given_self__then_password_generated(self, client_tester: FlaskClient):
        user: User = Helpers.create_user("test")
        password = user.generate_password()
        assert re.match(r"^[a-zA-Z\d]{12}$", password)

    def test__to_dict__given_self__then_dict_returned(self, client_tester: FlaskClient):
        user: User = Helpers.create_user("test")
        assert user.to_dict() == {"first_login": True, "id": 2, "is_admin": False, "mfa": False, "username": "test"}


class TestSettings:
    def test__to_dict__given_self__then_dict_returned(self, client_tester: FlaskClient):
        settings: Settings = db.session.query(Settings).one()
        assert settings.to_dict() == {
            "smtp_host": None,
            "smtp_port": None,
            "starttls": None,
            "ssl_tls": None,
            "mail_from": None,
            "mail_to": None,
            "smtp_user": None,
            "smtp_status": None,
            "webhook_url": None,
            "webhook_type": None,
        }


class TestUserLoaderCallback:
    def test__given_jwt__then_user_returned(self, client_tester: FlaskClient):
        user: User = user_loader_callback({}, {"sub": "admin"})
        admin: User = db.session.query(User).filter_by(username="admin").one()
        assert user is admin


class TestCheckIfTokenInBlocklist:
    def test__given_access_token__then_false_returned(self, client_tester: FlaskClient):
        token_in_blocklist = check_if_token_in_blocklist({}, {"type": "access"})
        assert token_in_blocklist is False

    def test__given_refresh_token__when_jti_blocked__then_true_returned(self, client_tester: FlaskClient):
        Helpers.create_blocked_jti("abc123")
        token_in_blocklist = check_if_token_in_blocklist({}, {"type": "refresh", "jti": "abc123"})
        assert token_in_blocklist is True


class TestInitApp:
    def test__given_app__when_already_init__then_do_nothing(self, client_tester: FlaskClient):
        assert db.session.query(User).count() == 1
        assert db.session.query(Settings).count() == 1
        assert db.session.query(BlockedJti).count() == 0
        init_app(client_tester.application)
        assert db.session.query(User).count() == 1
        assert db.session.query(Settings).count() == 1
        assert db.session.query(BlockedJti).count() == 0

    @pytest.mark.no_db_init
    def test__given_app__when_need_init__then_db_modified(self, client_tester: FlaskClient):
        Helpers.create_blocked_jti("abc123")
        assert db.session.query(User).count() == 0
        assert db.session.query(Settings).count() == 0
        assert db.session.query(BlockedJti).count() == 1
        init_app(client_tester.application)
        assert db.session.query(User).count() == 1
        assert db.session.query(Settings).count() == 1
        assert db.session.query(BlockedJti).count() == 0
