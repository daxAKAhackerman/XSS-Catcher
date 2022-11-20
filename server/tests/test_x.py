import json
from unittest import mock

from app import db
from app.models import XSS, Client, Settings
from flask.testing import FlaskClient
from tests.helpers import create_client, set_settings


def test__catch_xss__given_non_existant_user_id__then_200_returned(client_tester: FlaskClient):
    response = client_tester.get("/api/x/r/abc")
    assert response.json == {"msg": "OK"}
    assert response.status_code == 200


def test__catch_xss__given_existant_user_id__then_200_returned(client_tester: FlaskClient):
    client: Client = create_client("test")
    response = client_tester.get(f"/api/x/r/{client.uid}")
    assert response.json == {"msg": "OK"}
    assert response.status_code == 200


def test__catch_xss__given_reflected_xss__then_correct_type_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.get(f"/api/x/r/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    assert xss.xss_type == "reflected"


def test__catch_xss__given_stored_xss__then_correct_type_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.get(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    assert xss.xss_type == "stored"


def test__catch_xss__given_x_forwarded_for_header__then_correct_ip_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.get(f"/api/x/s/{client.uid}", headers={"X-Forwarded-For": "1.1.1.1"})
    xss: XSS = db.session.query(XSS).first()
    assert xss.ip_addr == "1.1.1.1"


def test__catch_xss__given_no_x_forwarded_for_header__then_correct_ip_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.get(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    assert xss.ip_addr == "127.0.0.1"


def test__catch_xss__given_query_string_parameters__then_data_captured(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.get(f"/api/x/s/{client.uid}?param=value")
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"param": "value"}


def test__catch_xss__given_json_data__then_data_captured(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"param": "value"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"param": "value"}


def test__catch_xss__given_form_data__then_data_captured(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", data={"param": "value"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"param": "value"}


def test__catch_xss__given_headers__then_headers_captured(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", headers={"Header-Name": "HeaderValue"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.headers)["Header-Name"] == "HeaderValue"


def test__catch_xss__given_empty_data__then_not_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"cookies": ""})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {}


def test__catch_xss__given_cookies__then_cookies_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"cookies": "Cookie1=Value1; Cookie2=Value2"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"cookies": {"Cookie1": "Value1", "Cookie2": "Value2"}}


def test__catch_xss__given_local_storage__then_local_storage_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"local_storage": json.dumps({"Param1": "Value1", "Param2": "Value2"})})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"local_storage": {"Param1": "Value1", "Param2": "Value2"}}


def test__catch_xss__given_session_storage__then_session_storage_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"session_storage": json.dumps({"Param1": "Value1", "Param2": "Value2"})})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"session_storage": {"Param1": "Value1", "Param2": "Value2"}}


def test__catch_xss__given_dom__then_dom_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"dom": "<body><h1>Hello World</h1></body>"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.data) == {"dom": "<html>\n<body><h1>Hello World</h1></body>\n</html>"}


def test__catch_xss__given_tags__then_tags_stored(client_tester: FlaskClient):
    client: Client = create_client("test")
    client_tester.post(f"/api/x/s/{client.uid}", json={"tags": "tag1,tag2"})
    xss: XSS = db.session.query(XSS).first()
    assert json.loads(xss.tags) == ["tag1", "tag2"]


@mock.patch("app.api.x.send_mail")
def test__catch_xss__given_xss__when_global_mail_to_configured__then_mail_sent(send_mail_mocker: mock.MagicMock, client_tester: FlaskClient):
    client: Client = create_client("test")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca", mail_to="test@example.com")
    client_tester.post(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    send_mail_mocker.assert_called_once_with(xss=xss)
    assert settings.smtp_status == True


@mock.patch("app.api.x.send_mail")
def test__catch_xss__given_xss__when_client_mail_to_configured__then_mail_sent(send_mail_mocker: mock.MagicMock, client_tester: FlaskClient):
    client: Client = create_client("test", mail_to="test@example.com")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca")
    client_tester.post(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    send_mail_mocker.assert_called_once_with(xss=xss)
    assert settings.smtp_status == True


@mock.patch("app.api.x.send_mail", side_effect=ValueError)
@mock.patch("app.api.x.logger")
def test__catch_xss__given_xss__when_client_mail_to_configured_but_sending_error_occurs__then_smtp_status_set_to_false(
    logger_mocker: mock.MagicMock, send_mail_mocker: mock.MagicMock, client_tester: FlaskClient
):
    client: Client = create_client("test", mail_to="test@example.com")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca")
    client_tester.post(f"/api/x/s/{client.uid}")
    assert settings.smtp_status == False
    logger_mocker.error.assert_called_once()


@mock.patch("app.api.x.send_webhook")
def test__catch_xss__given_xss__when_global_webhook_configured__then_webhook_sent(send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient):
    client: Client = create_client("test")
    set_settings(webhook_url="http://test.com")
    client_tester.post(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    send_webhook_mocker.assert_called_once_with(xss=xss)


@mock.patch("app.api.x.send_webhook")
def test__catch_xss__given_xss__when_client_webhook_configured__then_webhook_sent(send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient):
    client: Client = create_client("test", webhook_url="http://test.com")
    client_tester.post(f"/api/x/s/{client.uid}")
    xss: XSS = db.session.query(XSS).first()
    send_webhook_mocker.assert_called_once_with(xss=xss)


@mock.patch("app.api.x.send_webhook", side_effect=ValueError)
@mock.patch("app.api.x.logger")
def test__catch_xss__given_xss__when_client_webhook_configured_but_sending_error_occurs__then_error_logged(
    logger_mocker: mock.MagicMock, send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient
):
    client: Client = create_client("test", webhook_url="http://test.com")
    client_tester.post(f"/api/x/s/{client.uid}")
    logger_mocker.error.assert_called_once()
