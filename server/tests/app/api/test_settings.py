from unittest import mock

from app import db
from app.models import Settings
from flask.testing import FlaskClient
from tests.helpers import login, set_settings


def test__settings_get__given_request__then_settings_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.get("/api/settings", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json == {
        "mail_from": None,
        "mail_to": None,
        "smtp_host": None,
        "smtp_port": None,
        "smtp_status": None,
        "smtp_user": None,
        "ssl_tls": False,
        "starttls": False,
        "webhook_url": None,
    }
    assert response.status_code == 200


def test__settings_patch__given_smtp_host__when_smtp_port_missing__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch("/api/settings", json={"smtp_host": "127.0.0.1"}, headers={"Authorization": f"Bearer {access_token}"})
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_host == None
    assert response.json == {"msg": "Missing SMTP port"}
    assert response.status_code == 400


def test__settings_patch__given_both_starttls_and_ssl_tls__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(
        "/api/settings",
        json={"starttls": True, "ssl_tls": True, "smtp_host": "127.0.0.1", "smtp_port": 465, "mail_from": "test@example.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    settings: Settings = db.session.query(Settings).one()
    assert settings.starttls is False
    assert settings.ssl_tls is False
    assert response.json == {"msg": "Cannot use STARTTLS and SSL/TLS at the same time"}
    assert response.status_code == 400


def test__settings_patch__given_smtp_host__when_mail_from_missing__then_400_returned(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch("/api/settings", json={"smtp_host": "127.0.0.1", "smtp_port": 465}, headers={"Authorization": f"Bearer {access_token}"})
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_host == None
    assert response.json == {"msg": "Missing sender address"}
    assert response.status_code == 400


def test__settings_patch__given_all_fields__when_fields_are_valid__then_settings_edited(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
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
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_host == "127.0.0.1"
    assert settings.smtp_port == 465
    assert settings.mail_to == "mail_to@example.com"
    assert settings.mail_from == "mail_from@example.com"
    assert settings.smtp_user == "user"
    assert settings.smtp_pass == "pass"
    assert settings.webhook_url == "http://127.0.0.1"
    assert settings.ssl_tls is True
    assert settings.starttls is False
    assert response.json == {"msg": "Configuration saved successfully"}
    assert response.status_code == 200


def test__settings_patch__given_all_smtp_fields_but_smtp_host__then_all_smtp_settings_set_to_none(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(
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
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_host is None
    assert settings.smtp_port is None
    assert settings.mail_to is None
    assert settings.mail_from is None
    assert settings.smtp_user is None
    assert settings.smtp_pass is None
    assert settings.starttls is False


def test__settings_patch__given_smtp_pass__when_smtp_user_missing__then_credentials_set_to_none(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.patch(
        "/api/settings",
        json={
            "smtp_host": "127.0.0.1",
            "smtp_port": 25,
            "mail_from": "mail_from@example.com",
            "smtp_pass": "pass",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_pass is None


def test__settings_patch__given_mail_to__when_empty_string__then_field_set_to_none(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", mail_to="abc@example.com")
    response = client_tester.patch(
        "/api/settings",
        json={"mail_to": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert settings.mail_to is None


def test__settings_patch__given_smtp_user__when_empty_string__then_field_set_to_none(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", smtp_user="user")
    response = client_tester.patch(
        "/api/settings",
        json={"smtp_user": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert settings.smtp_user is None


def test__settings_patch__given_webhook_url__when_empty_string__then_field_set_to_none(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    settings: Settings = set_settings(webhook_url="http://127.0.0.1")
    response = client_tester.patch(
        "/api/settings",
        json={"webhook_url": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert settings.webhook_url is None


def test__settings_patch__given_empty_smtp_host__then_smtp_configuration_reset(client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")
    response = client_tester.patch(
        "/api/settings",
        json={"smtp_host": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert settings.smtp_host is None
    assert settings.smtp_port is None
    assert settings.mail_from is None


@mock.patch("app.api.settings.EmailTestNotification")
def test__smtp_test_post__given_mail_to__then_configuration_successfully_tested(EmailTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/settings/smtp_test", json={"mail_to": "test@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    settings: Settings = db.session.query(Settings).one()
    EmailTestNotification_mocker.assert_called_once_with(email_to="test@example.com")
    EmailTestNotification_mocker.return_value.send.assert_called_once()
    assert settings.smtp_status == True
    assert response.json == {"msg": "SMTP configuration test successful"}
    assert response.status_code == 200


@mock.patch("app.api.settings.EmailTestNotification", side_effect=ValueError)
def test__smtp_test_post__given_mail_to__when_send_test_mail_fails__then_configuration_test_fails(
    EmailTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient
):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/settings/smtp_test", json={"mail_to": "test@example.com"}, headers={"Authorization": f"Bearer {access_token}"})
    settings: Settings = db.session.query(Settings).one()
    assert settings.smtp_status == False
    assert response.json == {"msg": "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it. "}
    assert response.status_code == 400


@mock.patch("app.api.settings.WebhookTestNotification")
def test__webhook_test_post__given_webhook_url__then_test_successful(WebhookTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post("/api/settings/webhook_test", json={"webhook_url": "https://test.com"}, headers={"Authorization": f"Bearer {access_token}"})
    WebhookTestNotification_mocker.assert_called_once_with(webhook_url="https://test.com")
    WebhookTestNotification_mocker.return_value.send.assert_called_once()
    assert response.json == {"msg": "Webhook configuration test successful"}
    assert response.status_code == 200


@mock.patch("app.api.settings.WebhookTestNotification", side_effect=ValueError)
def test__webhook_test_post__given_webhook_url__when_bad_url__then_test_fails(WebhookTestNotification_mocker: mock.MagicMock, client_tester: FlaskClient):
    access_token, refresh_token = login(client_tester, "admin", "xss")
    response = client_tester.post(
        "/api/settings/webhook_test", json={"webhook_url": "https://donotexist.com"}, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.json == {"msg": "Could not send test webhook"}
    assert response.status_code == 400
