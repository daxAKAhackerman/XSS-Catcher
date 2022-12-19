from email.mime.text import MIMEText
from unittest import mock

from app.models import XSS, Client, Settings
from app.utils import (
    _send_mail,
    _send_webhook,
    send_test_mail,
    send_test_webhook,
    send_xss_mail,
    send_xss_webhook,
)
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import create_client, create_user, create_xss, login, set_settings


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


@mock.patch("app.utils._send_mail")
def test__send_xss_mail__given_xss___when_global_mail_to__then_send_mail_called(_send_mail_mocker: mock.MagicMock, client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", mail_to="abc@example.com")
    create_client("test")
    xss: XSS = create_xss()
    message = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Captured XSS for client test\nTo: abc@example.com\nFrom: XSS Catcher <test@example.com>\n\nXSS Catcher just caught a new stored XSS for client test! Go check it out!'

    send_xss_mail(xss)

    _send_mail_mocker.assert_called_once_with(settings, "test@example.com", "abc@example.com", mock.ANY)
    assert _send_mail_mocker.call_args[0][3].as_string() == message


@mock.patch("app.utils._send_mail")
def test__send_xss_mail__given_xss___when_client_mail_to__then_send_mail_called(_send_mail_mocker: mock.MagicMock, client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")
    create_client("test", mail_to="abc@example.com")
    xss: XSS = create_xss()
    message = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Captured XSS for client test\nTo: abc@example.com\nFrom: XSS Catcher <test@example.com>\n\nXSS Catcher just caught a new stored XSS for client test! Go check it out!'

    send_xss_mail(xss)

    _send_mail_mocker.assert_called_once_with(settings, "test@example.com", "abc@example.com", mock.ANY)
    assert _send_mail_mocker.call_args[0][3].as_string() == message


@mock.patch("app.utils._send_mail")
def test__send_test_mail__given_mail_to___then_send_mail_called(_send_mail_mocker: mock.MagicMock, client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")
    message = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: XSS Catcher mail test\nTo: abc@example.com\nFrom: XSS Catcher <test@example.com>\n\nThis is a test email from XSS catcher. If you are getting this, it\'s because your SMTP configuration works.'

    send_test_mail("abc@example.com")

    _send_mail_mocker.assert_called_once_with(settings, "test@example.com", "abc@example.com", mock.ANY)
    assert _send_mail_mocker.call_args[0][3].as_string() == message


@mock.patch("app.utils.smtplib")
@mock.patch("app.utils.ssl")
def test___send_mail__given_mail_properties__when_ssl_tls_and_auth__then_mail_sent(
    ssl_mocker: mock.MagicMock, smtplib_mocker: mock.MagicMock, client_tester: FlaskClient
):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", ssl_tls=True, smtp_user="test", smtp_pass="password")
    _send_mail(settings, "test@example.com", "abc@example.com", MIMEText("test"))

    smtplib_mocker.SMTP_SSL.assert_called_once_with(settings.smtp_host, settings.smtp_port, context=ssl_mocker.create_default_context.return_value)

    server: mock.MagicMock = smtplib_mocker.SMTP_SSL.return_value.__enter__.return_value

    server.login.assert_called_once_with(settings.smtp_user, settings.smtp_pass)
    server.sendmail.assert_called_once_with(
        "test@example.com", "abc@example.com", 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\ntest'
    )


@mock.patch("app.utils.smtplib")
def test___send_mail__given_mail_properties__when_starttls_and_auth__then_mail_sent(smtplib_mocker: mock.MagicMock, client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", starttls=True, smtp_user="test", smtp_pass="password")
    _send_mail(settings, "test@example.com", "abc@example.com", MIMEText("test"))

    smtplib_mocker.SMTP.assert_called_once_with(settings.smtp_host, settings.smtp_port)

    server: mock.MagicMock = smtplib_mocker.SMTP.return_value.__enter__.return_value

    server.login.assert_called_once_with(settings.smtp_user, settings.smtp_pass)
    server.starttls.assert_called_once()
    server.sendmail.assert_called_once_with(
        "test@example.com", "abc@example.com", 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\ntest'
    )


@freeze_time("2000-01-01")
@mock.patch("app.utils._send_webhook")
def test__send_xss_webhook__given_xss__when_global_webhook__then_webhook_sent(_send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient):
    settings: Settings = set_settings(webhook_url="http://127.0.0.1")
    create_client("test")
    xss: XSS = create_xss()

    send_xss_webhook(xss)
    _send_webhook_mocker.assert_called_once_with(
        "http://127.0.0.1",
        {
            "text": "XSS Catcher just caught a new stored XSS for client test",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": ":rotating_light: *XSS Catcher just caught a new XSS* :rotating_light:"}},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": ":bust_in_silhouette: *Client:* test"},
                        {"type": "mrkdwn", "text": ":lock: *XSS type:* stored"},
                        {"type": "mrkdwn", "text": ":calendar: *Timestamp:* 2000-01-01 00:00:00"},
                        {"type": "mrkdwn", "text": ":globe_with_meridians: *IP address:* 127.0.0.1"},
                        {"type": "mrkdwn", "text": ":label: *Tags:* "},
                        {"type": "mrkdwn", "text": ":floppy_disk: *Data collected:* 0"},
                    ],
                },
                {"type": "divider"},
            ],
        },
    )


@freeze_time("2000-01-01")
@mock.patch("app.utils._send_webhook")
def test__send_xss_webhook__given_xss__when_client_webhook__then_webhook_sent(_send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient):
    create_client("test", webhook_url="http://127.0.0.1")
    xss: XSS = create_xss()

    send_xss_webhook(xss)
    _send_webhook_mocker.assert_called_once_with(
        "http://127.0.0.1",
        {
            "text": "XSS Catcher just caught a new stored XSS for client test",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": ":rotating_light: *XSS Catcher just caught a new XSS* :rotating_light:"}},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": ":bust_in_silhouette: *Client:* test"},
                        {"type": "mrkdwn", "text": ":lock: *XSS type:* stored"},
                        {"type": "mrkdwn", "text": ":calendar: *Timestamp:* 2000-01-01 00:00:00"},
                        {"type": "mrkdwn", "text": ":globe_with_meridians: *IP address:* 127.0.0.1"},
                        {"type": "mrkdwn", "text": ":label: *Tags:* "},
                        {"type": "mrkdwn", "text": ":floppy_disk: *Data collected:* 0"},
                    ],
                },
                {"type": "divider"},
            ],
        },
    )


@mock.patch("app.utils._send_webhook")
def test__send_test_webhook__given_webhook_url__then_webhook_sent(_send_webhook_mocker: mock.MagicMock, client_tester: FlaskClient):
    send_test_webhook("http://127.0.0.1")
    _send_webhook_mocker.assert_called_once_with(
        "http://127.0.0.1", {"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}
    )


@mock.patch("app.utils.requests")
def test___send_webhook__given_webhook_properties__then_webhook_sent(requests_mocker: mock.MagicMock):
    _send_webhook("http://127.0.0.1", {"key": "value"})
    requests_mocker.post.assert_called_once_with(url="http://127.0.0.1", json={"key": "value"})
