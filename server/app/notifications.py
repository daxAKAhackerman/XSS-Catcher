import json
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import IntEnum
from typing import Any, cast

import requests
from app import db
from app.schemas import XSS, Client, Settings, User
from jinja2 import Environment, FileSystemLoader


class WebhookType(IntEnum):
    SLACK = 0
    DISCORD = 1
    AUTOMATION = 2


class EmailNotification:
    email_to: str
    email_from: str
    settings: Settings

    def __init__(self) -> None:
        self.settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        if self.settings.mail_from is None:
            raise Exception("Cannot initialize EmailNotification without mail_from setting")
        else:
            self.email_from = self.settings.mail_from

    @property
    def message(self) -> Any:  # pragma: no cover
        raise NotImplementedError

    def send(self) -> None:
        if self.settings.smtp_host is None or self.settings.smtp_port is None:
            raise Exception("Cannot send EmailNotification without smtp_host and smtp_port settings")

        user = self.settings.smtp_user
        password = self.settings.smtp_pass

        if self.settings.ssl_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port, context=context) as server:
                if user is not None and password is not None:
                    server.login(user, password)
                server.sendmail(self.email_from, self.email_to, self.message.as_string())

        else:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                if self.settings.starttls:
                    server.starttls()
                if user is not None and password is not None:
                    server.login(user, password)
                server.sendmail(self.email_from, self.email_to, self.message.as_string())


class EmailXssNotification(EmailNotification):
    xss: XSS
    client: Client

    def __init__(self, xss: XSS) -> None:
        super().__init__()
        self.xss = xss
        self.client = cast(Client, self.xss.client)  # type: ignore
        if email_to := self.client.mail_to or self.settings.mail_to:
            self.email_to = email_to
        else:
            raise Exception("Cannot initialize EmailXssNotification without global or client mail_to setting")

    @property
    def message(self) -> MIMEMultipart:
        j2_environment = Environment(loader=FileSystemLoader("app/templates"))
        email_template = j2_environment.get_template("email_notification.html")

        text_content = f"XSS Catcher just caught a new {self.xss.xss_type} XSS for client {self.client.name}"
        html_content = email_template.render(
            client_name=self.client.name,
            xss_type=self.xss.xss_type,
            timestamp=datetime.fromtimestamp(self.xss.timestamp),
            ip_address=self.xss.ip_addr,
            tags=", ".join(json.loads(self.xss.tags)),
            nb_data=len(json.loads(self.xss.data)),
        )
        message = MIMEMultipart("alternative")
        message["To"] = self.email_to
        message["From"] = f"XSS Catcher <{self.email_from}>"
        message["Subject"] = f"Captured {self.xss.xss_type} XSS for client {self.client.name}"
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        return message


class EmailTestNotification(EmailNotification):
    def __init__(self, email_to: str) -> None:
        super().__init__()
        self.email_to = email_to

    @property
    def message(self) -> MIMEText:
        message = MIMEText("This is a test email from XSS catcher. If you are getting this, it's because your SMTP configuration works.")
        message["To"] = self.email_to
        message["From"] = f"XSS Catcher <{self.email_from}>"
        message["Subject"] = "XSS Catcher test mail"
        return message


class WebhookNotification:
    settings: Settings
    webhook_type: int
    webhook_url: str

    def __init__(self) -> None:
        self.settings: Settings = db.session.execute(db.select(Settings)).scalar_one()
        if self.settings.webhook_type is None:
            raise Exception("Cannot initialize WebhookNotification without webhook_type setting")
        else:
            self.webhook_type = self.settings.webhook_type

    @property
    def message(self) -> dict[str, Any]:
        match self.webhook_type:
            case WebhookType.SLACK:
                return self.slack_message
            case WebhookType.DISCORD:
                return self.discord_message
            case _:
                return self.automation_message

    @property
    def slack_message(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    @property
    def discord_message(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    @property
    def automation_message(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def send(self) -> None:
        requests.post(url=self.webhook_url, json=self.message)


class WebhookXssNotification(WebhookNotification):
    xss: XSS
    client: Client
    owner: User

    def __init__(self, xss: XSS) -> None:
        super().__init__()
        self.xss = xss
        self.client = cast(Client, self.xss.client)  # type:ignore
        self.owner = cast(User, self.client.owner)  # type:ignore
        if webhook_url := self.client.webhook_url or self.settings.webhook_url:
            self.webhook_url = webhook_url
        else:
            raise Exception("Cannot initialize WebhookXssNotification without global or client webhook_url setting")

    @property
    def slack_message(self) -> dict[str, Any]:
        return {
            "text": f"XSS Catcher just caught a new {self.xss.xss_type} XSS for client {self.client.name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*XSS Catcher just caught a new XSS*",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f":bust_in_silhouette: *Client:* {self.client.name}"},
                        {"type": "mrkdwn", "text": f":lock: *XSS type:* {self.xss.xss_type}"},
                        {"type": "mrkdwn", "text": f":calendar: *Timestamp:* {datetime.fromtimestamp(self.xss.timestamp)} (UTC)"},
                        {"type": "mrkdwn", "text": f":globe_with_meridians: *IP address:* {self.xss.ip_addr}"},
                        {"type": "mrkdwn", "text": f":label: *Tags:* {', '.join(json.loads(self.xss.tags or '[]')) or '_None_'}"},
                        {"type": "mrkdwn", "text": f":floppy_disk: *Data collected:* {len(json.loads(self.xss.data or '{}'))}"},
                    ],
                },
                {"type": "divider"},
            ],
        }

    @property
    def discord_message(self) -> dict[str, Any]:
        return {
            "content": "**XSS Catcher just caught a new XSS**",
            "embeds": [
                {
                    "fields": [
                        {"inline": True, "name": ":bust_in_silhouette: **Client**", "value": self.client.name},
                        {"inline": True, "name": ":lock: **XSS type**", "value": self.xss.xss_type},
                        {"inline": True, "name": ":calendar: **Timestamp**", "value": f"{datetime.fromtimestamp(self.xss.timestamp)} (UTC)"},
                        {"inline": True, "name": ":globe_with_meridians: **IP address**", "value": self.xss.ip_addr},
                        {"inline": True, "name": ":label: **Tags**", "value": ", ".join(json.loads(self.xss.tags)) or "*None*"},
                        {"inline": True, "name": ":floppy_disk: **Data collected**", "value": len(json.loads(self.xss.data))},
                    ],
                }
            ],
        }

    @property
    def automation_message(self) -> dict[str, Any]:
        return {
            "xss": {
                "id": self.xss.id,
                "ip_address": self.xss.ip_addr,
                "tags": json.loads(self.xss.tags),
                "timestamp": self.xss.timestamp,
                "type": self.xss.xss_type,
                "nb_of_collected_data": len(json.loads(self.xss.data)),
                "captured_data": list(json.loads(self.xss.data).keys()),
                "captured_headers": list(json.loads(self.xss.headers).keys()),
            },
            "client": {"id": self.client.id, "uid": self.client.uid, "name": self.client.name, "description": self.client.description},
            "user": {
                "id": self.owner.id,
                "username": self.owner.username,
                "admin": self.owner.is_admin,
            },
        }


class WebhookTestNotification(WebhookNotification):
    def __init__(self, webhook_url: str) -> None:
        super().__init__()
        self.webhook_url = webhook_url

    @property
    def slack_message(self) -> dict[str, str]:
        return {"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}

    @property
    def discord_message(self) -> dict[str, str]:
        return {"content": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}

    @property
    def automation_message(self) -> dict[str, str]:
        return {"msg": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}
