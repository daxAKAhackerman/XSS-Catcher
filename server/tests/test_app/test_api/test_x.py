import json
from unittest import mock

from app import db
from app.schemas import XSS, Client, Settings
from flask.testing import FlaskClient
from tests.helpers import Helpers


class TestCatchXss:
    def test__given_non_existant_user_id__then_200_returned(self, client_tester: FlaskClient):
        response = client_tester.get("/api/x/r/abc")
        assert response.json == {"msg": "OK"}
        assert response.status_code == 200

    def test__given_existant_user_id__then_200_returned(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        response = client_tester.get(f"/api/x/r/{client.uid}")
        assert response.json == {"msg": "OK"}
        assert response.status_code == 200


class TestSaveXss:
    def test__given_reflected_xss__then_correct_type_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.get(f"/api/x/r/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert xss.xss_type == "reflected"

    def test__given_stored_xss__then_correct_type_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.get(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert xss.xss_type == "stored"

    def test__given_x_forwarded_for_header__then_correct_ip_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.get(f"/api/x/s/{client.uid}", headers={"X-Forwarded-For": "1.1.1.1"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert xss.ip_addr == "1.1.1.1"

    def test__given_no_x_forwarded_for_header__then_correct_ip_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.get(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert xss.ip_addr == "127.0.0.1"

    def test__given_query_string_parameters__then_data_captured(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.get(f"/api/x/s/{client.uid}?param=value")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"param": "value"}

    def test__given_json_data__then_data_captured(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"param": "value"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"param": "value"}

    def test__given_form_data__then_data_captured(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", data={"param": "value"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"param": "value"}

    def test__given_headers__then_headers_captured(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", headers={"Header-Name": "HeaderValue"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.headers)["Header-Name"] == "HeaderValue"

    def test__given_empty_data__then_not_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"cookies": ""})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {}

    def test__given_cookies__then_cookies_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"cookies": "Cookie1=Value1; Cookie2=Value2"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"cookies": {"Cookie1": "Value1", "Cookie2": "Value2"}}

    def test__given_local_storage__then_local_storage_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"local_storage": json.dumps({"Param1": "Value1", "Param2": "Value2"})})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"local_storage": {"Param1": "Value1", "Param2": "Value2"}}

    def test__given_session_storage__then_session_storage_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"session_storage": json.dumps({"Param1": "Value1", "Param2": "Value2"})})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"session_storage": {"Param1": "Value1", "Param2": "Value2"}}

    def test__given_dom__then_dom_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"dom": "<body><h1>Hello World</h1></body>"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.data) == {"dom": "<html>\n<body><h1>Hello World</h1></body>\n</html>"}

    def test__given_tags__then_tags_stored(self, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        client_tester.post(f"/api/x/s/{client.uid}", json={"tags": "tag1,tag2"})
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        assert json.loads(xss.tags) == ["tag1", "tag2"]


class TestHandleNotifications:
    @mock.patch("app.api.x.EmailXssNotification")
    def test__given_xss__when_global_mail_to_configured__then_mail_sent(self, EmailXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        settings: Settings = Helpers.set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca", mail_to="test@example.com")
        client_tester.post(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        EmailXssNotification_mocker.assert_called_once_with(xss=xss)
        EmailXssNotification_mocker.return_value.send.assert_called_once
        assert settings.smtp_status is True

    @mock.patch("app.api.x.EmailXssNotification")
    def test__given_xss__when_client_mail_to_configured__then_mail_sent(self, EmailXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test", mail_to="test@example.com")
        settings: Settings = Helpers.set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca")
        client_tester.post(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        EmailXssNotification_mocker.assert_called_once_with(xss=xss)
        EmailXssNotification_mocker.return_value.send.assert_called_once
        assert settings.smtp_status is True

    @mock.patch("app.api.x.EmailXssNotification", side_effect=ValueError)
    def test__given_xss__when_client_mail_to_configured_but_sending_error_occurs__then_smtp_status_set_to_false(
        self, EmailXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient
    ):
        client: Client = Helpers.create_client("test", mail_to="test@example.com")
        settings: Settings = Helpers.set_settings(smtp_host="127.0.0.1", smtp_port="25", mail_from="dax@hackerman.ca")
        client_tester.post(f"/api/x/s/{client.uid}")
        assert settings.smtp_status is False

    @mock.patch("app.api.x.WebhookXssNotification")
    def test__given_xss__when_global_webhook_configured__then_webhook_sent(self, WebhookXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test")
        Helpers.set_settings(webhook_url="http://test.com")
        client_tester.post(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        WebhookXssNotification_mocker.assert_called_once_with(xss=xss)
        WebhookXssNotification_mocker.return_value.send.assert_called_once()

    @mock.patch("app.api.x.WebhookXssNotification")
    def test__given_xss__when_client_webhook_configured__then_webhook_sent(self, WebhookXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        client: Client = Helpers.create_client("test", webhook_url="http://test.com")
        client_tester.post(f"/api/x/s/{client.uid}")
        xss: XSS = db.session.execute(db.select(XSS)).scalar_one()
        WebhookXssNotification_mocker.assert_called_once_with(xss=xss)
        WebhookXssNotification_mocker.return_value.send.assert_called_once()

    @mock.patch("app.api.x.WebhookXssNotification", side_effect=ValueError)
    def test__given_xss__when_client_webhook_configured_but_sending_error_occurs__then_error_logged(
        self, WebhookXssNotification_mocker: mock.MagicMock, client_tester: FlaskClient
    ):
        client: Client = Helpers.create_client("test", webhook_url="http://test.com")
        client_tester.post(f"/api/x/s/{client.uid}")
