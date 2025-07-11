from unittest import mock

from app import db
from app.schemas import Settings
from flask.testing import FlaskClient
from tests.helpers import Helpers


class TestGetSettings:
    def test__given_request__then_settings_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.get("/api/settings", headers={"Authorization": f"Bearer {access_token}"})
        assert response.json == {
            "mail_from": None,
            "mail_to": None,
            "smtp_host": None,
            "smtp_port": None,
            "smtp_status": None,
            "smtp_user": None,
            "ssl_tls": None,
            "starttls": None,
            "webhook_url": None,
            "webhook_type": None,
        }
        assert response.status_code == 200


class TestEditSettings:
    def test__given_smtp_host__when_smtp_port_missing__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch("/api/settings", json={"smtp_host": "127.0.0.1"}, headers={"Authorization": f"Bearer {access_token}"})
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_host is None
        assert response.json == {"msg": "Missing SMTP port"}
        assert response.status_code == 400

    def test__given_both_starttls_and_ssl_tls__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch(
            "/api/settings",
            json={"starttls": True, "ssl_tls": True, "smtp_host": "127.0.0.1", "smtp_port": 465, "mail_from": "test@example.com"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.starttls is None
        assert settings.ssl_tls is None
        assert response.json == {"msg": "Cannot use STARTTLS and SSL/TLS at the same time"}
        assert response.status_code == 400

    def test__given_smtp_host__when_mail_from_missing__then_400_returned(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch("/api/settings", json={"smtp_host": "127.0.0.1", "smtp_port": 465}, headers={"Authorization": f"Bearer {access_token}"})
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_host is None
        assert response.json == {"msg": "Missing sender address"}
        assert response.status_code == 400

    def test__given_all_fields__when_fields_are_valid__then_settings_edited(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.patch(
            "/api/settings",
            json={
                "smtp_host": "127.0.0.1",
                "smtp_port": 465,
                "mail_to": "mail_to@example.com",
                "mail_from": "mail_from@example.com",
                "smtp_user": "user",
                "smtp_pass": "pass",
                "webhook_url": "http://127.0.0.1",
                "ssl_tls": True,
                "webhook_type": 1,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_host == "127.0.0.1"
        assert settings.smtp_port == 465
        assert settings.mail_to == "mail_to@example.com"
        assert settings.mail_from == "mail_from@example.com"
        assert settings.smtp_user == "user"
        assert settings.smtp_pass == "pass"
        assert settings.webhook_url == "http://127.0.0.1"
        assert settings.ssl_tls is True
        assert settings.starttls is None
        assert response.json == {"msg": "Configuration saved successfully"}
        assert response.status_code == 200

    def test__given_all_smtp_fields_but_smtp_host__then_all_smtp_settings_set_to_none(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        client_tester.patch(
            "/api/settings",
            json={
                "smtp_port": 465,
                "mail_to": "mail_to@example.com",
                "mail_from": "mail_from@example.com",
                "smtp_user": "user",
                "smtp_pass": "pass",
                "starttls": True,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_host is None
        assert settings.smtp_port is None
        assert settings.mail_to is None
        assert settings.mail_from is None
        assert settings.smtp_user is None
        assert settings.smtp_pass is None
        assert settings.starttls is None

    def test__given_smtp_pass__when_smtp_user_missing__then_credentials_set_to_none(self, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        client_tester.patch(
            "/api/settings",
            json={
                "smtp_host": "127.0.0.1",
                "smtp_port": 25,
                "mail_from": "mail_from@example.com",
                "smtp_pass": "pass",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_pass is None


class TestTestSmtpSettings:
    @mock.patch("app.api.settings.EmailTestNotification")
    def test__given_mail_to__then_configuration_successfully_tested(self, EmailTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/settings/smtp_test", json={"mail_to": "test@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        EmailTestNotification_mocker.assert_called_once_with(email_to="test@example.com")
        EmailTestNotification_mocker.return_value.send.assert_called_once()
        assert settings.smtp_status is True
        assert response.json == {"msg": "SMTP configuration test successful"}
        assert response.status_code == 200

    @mock.patch("app.api.settings.EmailTestNotification", side_effect=ValueError)
    def test__given_mail_to__when_send_test_mail_fails__then_configuration_test_fails(
        self, EmailTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient
    ):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post("/api/settings/smtp_test", json={"mail_to": "test@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
        settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        assert settings.smtp_status is False
        assert response.json == {"msg": "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it"}
        assert response.status_code == 400


class TestTestWehbookSettings:
    @mock.patch("app.api.settings.WebhookTestNotification")
    def test__given_webhook_url__then_test_successful(self, WebhookTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/settings/webhook_test", json={"webhook_url": "https://test.com"}, headers={"Authorization": f"Bearer {access_token}"}
        )
        WebhookTestNotification_mocker.assert_called_once_with(webhook_url="https://test.com")
        WebhookTestNotification_mocker.return_value.send.assert_called_once()
        assert response.json == {"msg": "Webhook configuration test successful"}
        assert response.status_code == 200

    @mock.patch("app.api.settings.WebhookTestNotification", side_effect=ValueError)
    def test__given_webhook_url__when_bad_url__then_test_fails(self, WebhookTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
        access_token, refresh_token = Helpers.login(client_tester, "admin", "xss")
        response = client_tester.post(
            "/api/settings/webhook_test", json={"webhook_url": "https://donotexist.com"}, headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.json == {"msg": "Could not send test webhook"}
        assert response.status_code == 400
