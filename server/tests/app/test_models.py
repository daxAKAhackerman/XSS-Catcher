import re
from unittest import mock

from app.models import XSS, Client, User
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import create_client, create_xss


def test__Client_summary__given_self__then_summary_returned(client_tester: FlaskClient):
    client: Client = create_client("test")
    create_xss(data={"TestKey": "TestValue", "TestKey2": "TestValue2"})
    assert client.summary() == {"owner_id": 1, "id": 1, "name": "test", "reflected": 0, "stored": 1, "data": 2}


def test__Client_to_dict__given_self__then_dict_returned(client_tester: FlaskClient):
    client: Client = create_client("test", mail_to="test@example.com", webhook_url="http://127.0.0.1")
    assert client.to_dict() == {"owner": "admin", "id": 1, "name": "test", "description": "", "mail_to": "test@example.com", "webhook_url": "http://127.0.0.1"}


def test__Client_generate_uid__given_self__then_uid_generated(client_tester: FlaskClient):
    client = Client()
    client.generate_uid()
    assert re.match(r"^[A-Za-z\d]{6}$", client.uid)


@freeze_time("2000-01-01")
def test__XSS_summary__given_self__then_summary_returned(client_tester: FlaskClient):
    xss: XSS = create_xss(tags=["tag1"])
    assert xss.summary() == {"id": 1, "ip_addr": "127.0.0.1", "timestamp": 946684800, "tags": ["tag1"]}


@freeze_time("2000-01-01")
def test__XSS_to_dict__given_self__then_dict_returned(client_tester: FlaskClient):
    xss: XSS = create_xss(tags=["tag1"], data={"TestKey": "TestValue"}, headers={"HeaderKey": "HeaderValue"})
    assert xss.to_dict() == {
        "id": 1,
        "headers": {"HeaderKey": "HeaderValue"},
        "ip_addr": "127.0.0.1",
        "data": {"TestKey": "TestValue"},
        "timestamp": 946684800,
        "tags": ["tag1"],
    }


@mock.patch("app.models.generate_password_hash")
def test__User_set_password__given_password__then_password_changed(generate_password_hash_mocker: mock.MagicMock, client_tester: FlaskClient):
    user = User()
    user.set_password("test")
    generate_password_hash_mocker.assert_called_once_with("test")
    assert user.password_hash == generate_password_hash_mocker.return_value


@mock.patch("app.models.check_password_hash")
def test__User_check_password__given_password__then_password_checked(check_password_hash_mocker: mock.MagicMock, client_tester: FlaskClient):
    user = User()
    password_check = user.check_password("test")
    check_password_hash_mocker.assert_called_once_with(user.password_hash, "test")
    assert password_check == check_password_hash_mocker.return_value


def test__User_generate_password__given_self__then_password_generated(client_tester: FlaskClient):
    user = User()
    password = user.generate_password()
    assert re.match(r"^[a-zA-Z\d]{12}$", password)
