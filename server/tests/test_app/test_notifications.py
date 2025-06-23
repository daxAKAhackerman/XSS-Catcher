import datetime
from email.mime.text import MIMEText
from typing import Iterator
from unittest import mock

import pytest
from app.models import XSS, Client, Settings
from app.notifications import (
    EmailNotification,
    EmailTestNotification,
    EmailXssNotification,
    WebhookTestNotification,
    WebhookXssNotification,
)
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import create_client, create_xss, set_settings


class TestEmailNotification:
    @pytest.fixture(autouse=True)
    def smtplib_mocker(self) -> Iterator[mock.MagicMock]:
        with mock.patch("app.notifications.smtplib") as smtplib_mocker:
            yield smtplib_mocker

    @pytest.fixture(autouse=True)
    def email_notification_message_mocker(self) -> Iterator[mock.PropertyMock]:
        with mock.patch("app.notifications.EmailNotification.message", new_callable=mock.PropertyMock) as email_notification_message_mocker:
            email_notification_message_mocker.return_value = MIMEText("This is a test")
            yield email_notification_message_mocker

    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        set_settings(mail_from="xss-catcher@hackerman.ca")
        email_notification = EmailNotification()

        assert email_notification.email_from == "xss-catcher@hackerman.ca"

    def test____init____given_self__when_no_mail_from__then_raise(self, client_tester: FlaskClient):
        set_settings()

        with pytest.raises(Exception):
            EmailNotification()

    @mock.patch("app.notifications.ssl")
    def test__send__when_ssl_tls_and_auth__then_email_sent(self, ssl_mocker: mock.MagicMock, smtplib_mocker: mock.MagicMock, client_tester: FlaskClient):
        settings: Settings = set_settings(
            smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", ssl_tls=True, smtp_user="test", smtp_pass="password"
        )

        email_notification = EmailNotification()
        email_notification.email_to = "test@test.com"
        email_notification.send()

        smtplib_mocker.SMTP_SSL.assert_called_once_with(settings.smtp_host, settings.smtp_port, context=ssl_mocker.create_default_context.return_value)

        server: mock.MagicMock = smtplib_mocker.SMTP_SSL.return_value.__enter__.return_value

        server.login.assert_called_once_with(settings.smtp_user, settings.smtp_pass)
        server.sendmail.assert_called_once_with(
            "test@example.com",
            "test@test.com",
            'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nThis is a test',
        )

    def test__send__when_starttls_and_auth__then_mail_sent(self, smtplib_mocker: mock.MagicMock, client_tester: FlaskClient):
        settings: Settings = set_settings(
            smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", starttls=True, smtp_user="test", smtp_pass="password"
        )

        email_notification = EmailNotification()
        email_notification.email_to = "test@test.com"
        email_notification.send()

        smtplib_mocker.SMTP.assert_called_once_with(settings.smtp_host, settings.smtp_port)

        server: mock.MagicMock = smtplib_mocker.SMTP.return_value.__enter__.return_value

        server.login.assert_called_once_with(settings.smtp_user, settings.smtp_pass)
        server.starttls.assert_called_once()
        server.sendmail.assert_called_once_with(
            "test@example.com",
            "test@test.com",
            'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nThis is a test',
        )


def test__EmailTestNotification_message(client_tester: FlaskClient):
    set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")

    email_test_notification = EmailTestNotification(email_to="test@test.com")

    assert (
        email_test_notification.message.as_string()
        == 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nTo: test@test.com\nFrom: XSS Catcher <test@example.com>\nSubject: XSS Catcher test mail\n\nThis is a test email from XSS catcher. If you are getting this, it\'s because your SMTP configuration works.'
    )


def test__EmailTestNotification___init__(client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")

    email_test_notification = EmailTestNotification(email_to="test@test.com")

    assert email_test_notification.settings is settings
    assert email_test_notification.email_from == "test@example.com"
    assert email_test_notification.email_to == "test@test.com"


@freeze_time("2000-01-01")
@mock.patch("app.notifications.Environment")
@mock.patch("app.notifications.FileSystemLoader")
def test__EmailXssNotification_message(FileSystemLoader_mocker: mock.MagicMock, Environment_mocker: mock.MagicMock, client_tester: FlaskClient):
    set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", mail_to="test@test.com")
    client: Client = create_client(name="test")
    xss: XSS = create_xss(client_id=client.id)

    render_mocker = Environment_mocker.return_value.get_template.return_value.render
    render_mocker.return_value = "<h1>Test</h1>"

    email_xss_notification = EmailXssNotification(xss=xss)

    message = email_xss_notification.message.as_string()

    render_mocker.assert_called_once_with(
        client_name="test", xss_type="stored", timestamp=datetime.datetime(2000, 1, 1, 0, 0), ip_address="127.0.0.1", tags="", nb_data=0
    )

    assert "MIME-Version: 1.0\nTo: test@test.com\nFrom: XSS Catcher <test@example.com>\nSubject: Captured stored XSS for client test" in message
    assert (
        'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nXSS Catcher just caught a new stored XSS for client test'
        in message
    )
    assert 'Content-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n<h1>Test</h1>' in message


def test__EmailXssNotification___init__(client_tester: FlaskClient):
    settings: Settings = set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")
    client: Client = create_client(name="test", mail_to="test@test.com")
    xss: XSS = create_xss(client_id=client.id)

    email_xss_notification = EmailXssNotification(xss=xss)

    assert email_xss_notification.settings is settings
    assert email_xss_notification.email_from == "test@example.com"
    assert email_xss_notification.email_to == "test@test.com"
    assert email_xss_notification.xss is xss


@mock.patch("app.notifications.requests")
def test__WebhookTestNotification_send__then_webhook_sent(requests_mocker: mock.MagicMock, client_tester: FlaskClient):
    set_settings()
    webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
    webhook_test_notification.send()

    requests_mocker.post.assert_called_once_with(
        url="http://localhost",
        json={"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."},
    )


def test__WebhookTestNotification_message__when_discord_type_in_settings__then_discord_message_returned(client_tester: FlaskClient):
    set_settings(webhook_type=1)
    webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
    assert webhook_test_notification.message == {
        "content": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
    }


def test__WebhookTestNotification_message__when_slack_type_in_settings__then_slack_message_returned(client_tester: FlaskClient):
    set_settings()
    webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
    assert webhook_test_notification.message == {
        "text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
    }


def test__WebhookTestNotification___init__(client_tester: FlaskClient):
    settings: Settings = set_settings()
    webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
    assert webhook_test_notification.webhook_url == "http://localhost"
    assert webhook_test_notification.settings is settings
    assert webhook_test_notification.webhook_type == 0


@freeze_time("2000-01-01")
def test__WebhookXssNotification_message__when_discord_type_in_settings__then_discord_message_returned(client_tester: FlaskClient):
    set_settings(webhook_url="http://localhost", webhook_type=1)
    client: Client = create_client(name="test")
    xss: XSS = create_xss(client_id=client.id)

    webhook_xss_notification = WebhookXssNotification(xss=xss)
    assert webhook_xss_notification.message == {
        "content": "**XSS Catcher just caught a new XSS**",
        "embeds": [
            {
                "fields": [
                    {"inline": True, "name": ":bust_in_silhouette: **Client**", "value": "test"},
                    {"inline": True, "name": ":lock: **XSS type**", "value": "stored"},
                    {"inline": True, "name": ":calendar: **Timestamp**", "value": "2000-01-01 00:00:00 (UTC)"},
                    {"inline": True, "name": ":globe_with_meridians: **IP address**", "value": "127.0.0.1"},
                    {"inline": True, "name": ":label: **Tags**", "value": "*None*"},
                    {"inline": True, "name": ":floppy_disk: **Data collected**", "value": 0},
                ]
            }
        ],
    }


@freeze_time("2000-01-01")
def test__WebhookXssNotification_message__when_slack_type_in_settings__then_slack_message_returned(client_tester: FlaskClient):
    set_settings(webhook_url="http://localhost")
    client: Client = create_client(name="test")
    xss: XSS = create_xss(client_id=client.id)

    webhook_xss_notification = WebhookXssNotification(xss=xss)
    assert webhook_xss_notification.message == {
        "text": "XSS Catcher just caught a new stored XSS for client test",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": "*XSS Catcher just caught a new XSS*"}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": ":bust_in_silhouette: *Client:* test"},
                    {"type": "mrkdwn", "text": ":lock: *XSS type:* stored"},
                    {"type": "mrkdwn", "text": ":calendar: *Timestamp:* 2000-01-01 00:00:00 (UTC)"},
                    {"type": "mrkdwn", "text": ":globe_with_meridians: *IP address:* 127.0.0.1"},
                    {"type": "mrkdwn", "text": ":label: *Tags:* _None_"},
                    {"type": "mrkdwn", "text": ":floppy_disk: *Data collected:* 0"},
                ],
            },
            {"type": "divider"},
        ],
    }


def test__WebhookXssNotification___init__(client_tester: FlaskClient):
    settings: Settings = set_settings()
    client: Client = create_client(name="test", webhook_url="http://localhost")
    xss: XSS = create_xss(client_id=client.id)

    webhook_xss_notification = WebhookXssNotification(xss=xss)
    assert webhook_xss_notification.webhook_url == "http://localhost"
    assert webhook_xss_notification.xss is xss
    assert webhook_xss_notification.settings is settings
    assert webhook_xss_notification.webhook_type == 0


@freeze_time("2000-01-01")
def test__WebhookXssNotification_message__when_automation_type_in_settings__then_automation_message_returned(client_tester: FlaskClient):
    set_settings(webhook_url="http://localhost", webhook_type=2)
    client: Client = create_client(name="test", uid="aaaaaa")
    xss: XSS = create_xss(client_id=client.id)

    webhook_xss_notification = WebhookXssNotification(xss=xss)
    assert webhook_xss_notification.message == {
        "xss": {
            "id": 1,
            "ip_address": "127.0.0.1",
            "tags": [],
            "timestamp": 946684800,
            "type": "stored",
            "nb_of_collected_data": 0,
            "captured_data": [],
            "captured_headers": [],
        },
        "client": {"id": 1, "uid": "aaaaaa", "name": "test", "description": ""},
        "user": {"id": 1, "username": "admin", "admin": True},
    }


def test__WebhookTestNotification_message__when_automation_type_in_settings__then_automation_message_returned(client_tester: FlaskClient):
    set_settings(webhook_type=2)
    webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
    assert webhook_test_notification.message == {
        "msg": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
    }
