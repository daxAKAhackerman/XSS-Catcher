import datetime
from email.mime.text import MIMEText
from typing import Iterator
from unittest import mock

import pytest
from app.notifications import (
    EmailNotification,
    EmailTestNotification,
    EmailXssNotification,
    WebhookNotification,
    WebhookTestNotification,
    WebhookXssNotification,
)
from app.schemas import XSS, Client, Settings
from flask.testing import FlaskClient
from freezegun import freeze_time
from tests.helpers import Helpers


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
        Helpers.set_settings(mail_from="xss-catcher@hackerman.ca")
        email_notification = EmailNotification()

        assert email_notification.email_from == "xss-catcher@hackerman.ca"

    def test____init____given_self__when_no_mail_from__then_raise(self, client_tester: FlaskClient):
        Helpers.set_settings()

        with pytest.raises(Exception):
            EmailNotification()

    @mock.patch("app.notifications.ssl")
    def test__send__when_ssl_tls_and_auth__then_email_sent(self, ssl_mocker: mock.MagicMock, smtplib_mocker: mock.MagicMock, client_tester: FlaskClient):
        settings: Settings = Helpers.set_settings(
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
        settings: Settings = Helpers.set_settings(
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

    def test__send__given_self__when_no_host_or_port__then_raise(self, client_tester: FlaskClient):
        Helpers.set_settings(mail_from="test@example.com")

        email_notification = EmailNotification()
        email_notification.email_to = "test@test.com"

        with pytest.raises(Exception):
            email_notification.send()


class TestEmailXssNotification:
    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        settings: Settings = Helpers.set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")
        client: Client = Helpers.create_client(name="test", mail_to="test@test.com")
        xss: XSS = Helpers.create_xss(client_id=client.id)

        email_xss_notification = EmailXssNotification(xss=xss)

        assert email_xss_notification.settings is settings
        assert email_xss_notification.email_from == "test@example.com"
        assert email_xss_notification.email_to == "test@test.com"
        assert email_xss_notification.xss is xss

    def test____init____given_self__when_no_mail_to__then_raise(self, client_tester: FlaskClient):
        Helpers.set_settings(mail_from="xss-catcher@hackerman.ca")
        client: Client = Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(client_id=client.id)

        with pytest.raises(Exception):
            EmailXssNotification(xss=xss)

    @freeze_time("2000-01-01")
    @mock.patch("app.notifications.Environment")
    @mock.patch("app.notifications.FileSystemLoader")
    def test__message__given_self__then_message_returned(
        self, FileSystemLoader_mocker: mock.MagicMock, Environment_mocker: mock.MagicMock, client_tester: FlaskClient
    ):
        Helpers.set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com", mail_to="test@test.com")
        client: Client = Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(client_id=client.id)

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


class TestEmailTestNotification:
    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        settings: Settings = Helpers.set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")

        email_test_notification = EmailTestNotification(email_to="test@test.com")

        assert email_test_notification.settings is settings
        assert email_test_notification.email_from == "test@example.com"
        assert email_test_notification.email_to == "test@test.com"

    def test__message__given_self__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(smtp_host="127.0.0.1", smtp_port=25, mail_from="test@example.com")

        email_test_notification = EmailTestNotification(email_to="test@test.com")

        assert (
            email_test_notification.message.as_string()
            == 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nTo: test@test.com\nFrom: XSS Catcher <test@example.com>\nSubject: XSS Catcher test mail\n\nThis is a test email from XSS catcher. If you are getting this, it\'s because your SMTP configuration works.'
        )


class TestWebhookNotification:
    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        settings: Settings = Helpers.set_settings(webhook_type=0)
        webhook_notification = WebhookNotification()

        assert webhook_notification.settings is settings
        assert webhook_notification.webhook_type == 0

    def test____init____given_self__when_no_webhook_type__then_raise(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_type=None)

        with pytest.raises(Exception):
            WebhookNotification()

    @pytest.mark.parametrize("webhook_type,message_func", [(0, "slack_message"), (1, "discord_message"), (2, "automation_message")])
    def test__message__given_self__then_correct_message_returned(
        self,
        webhook_type: int,
        message_func: str,
        client_tester: FlaskClient,
    ):
        Helpers.set_settings(webhook_type=webhook_type)

        with mock.patch(f"app.notifications.WebhookNotification.{message_func}", new_callable=mock.PropertyMock) as mocker:
            assert WebhookNotification().message is mocker.return_value

    @mock.patch("app.notifications.requests")
    @mock.patch("app.notifications.WebhookNotification.slack_message", new_callable=mock.PropertyMock, return_value={"text": "This is a test"})
    def test__send__given_self__then_webhook_sent(self, slack_message_mocker: mock.PropertyMock, requests_mocker: mock.MagicMock, client_tester: FlaskClient):
        Helpers.set_settings()
        webhook_notification = WebhookNotification()
        webhook_notification.webhook_url = "http://localhost"
        webhook_notification.send()

        requests_mocker.post.assert_called_once_with(
            url="http://localhost",
            json={"text": "This is a test"},
        )


class TestWebhookXssNotification:
    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        settings: Settings = Helpers.set_settings()
        client: Client = Helpers.create_client(name="test", webhook_url="http://localhost")
        xss: XSS = Helpers.create_xss(client_id=client.id)

        webhook_xss_notification = WebhookXssNotification(xss=xss)
        assert webhook_xss_notification.webhook_url == "http://localhost"
        assert webhook_xss_notification.xss is xss
        assert webhook_xss_notification.settings is settings
        assert webhook_xss_notification.client is client

    def test____init____given_self__when_missing_webhook_url__then_raise(self, client_tester: FlaskClient):
        Helpers.set_settings()
        client: Client = Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(client_id=client.id)

        with pytest.raises(Exception):
            WebhookXssNotification(xss=xss)

    @freeze_time("2000-01-01")
    def test__slack_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_url="http://localhost")
        client: Client = Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(client_id=client.id)

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

    @freeze_time("2000-01-01")
    def test__discord_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_url="http://localhost", webhook_type=1)
        client: Client = Helpers.create_client(name="test")
        xss: XSS = Helpers.create_xss(client_id=client.id)

        webhook_xss_notification = WebhookXssNotification(xss=xss)
        assert webhook_xss_notification.discord_message == {
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
    def test__automation_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_url="http://localhost", webhook_type=2)
        client: Client = Helpers.create_client(name="test", uid="aaaaaa")
        xss: XSS = Helpers.create_xss(client_id=client.id)

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


class TestWebhookTestNotification:
    def test____init____given_self__then_attributes_set(self, client_tester: FlaskClient):
        Helpers.set_settings()
        webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
        assert webhook_test_notification.webhook_url == "http://localhost"

    def test__slack_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings()
        webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
        assert webhook_test_notification.slack_message == {
            "text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
        }

    def test__discord_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_type=1)
        webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
        assert webhook_test_notification.discord_message == {
            "content": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
        }

    def test__automation_message__then_message_returned(self, client_tester: FlaskClient):
        Helpers.set_settings(webhook_type=1)
        webhook_test_notification = WebhookTestNotification(webhook_url="http://localhost")
        assert webhook_test_notification.automation_message == {
            "msg": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."
        }
