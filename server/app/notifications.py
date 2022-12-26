import json
import smtplib
import ssl
from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import IntEnum
from typing import Any, Dict

import requests
from app import db
from app.models import XSS, Settings
from jinja2 import Environment, FileSystemLoader


class WebhookType(IntEnum):
    SLACK = 0
    DISCORD = 1


class Notification(ABC):
    @property
    @abstractmethod
    def message(self) -> Any:  # pragma: no cover
        pass

    @abstractmethod
    def send(self) -> None:  # pragma: no cover
        pass


class EmailNotification(Notification, metaclass=ABCMeta):
    email_to: str
    email_from: str
    settings: Settings

    def __init__(self) -> None:
        self.settings: Settings = db.session.query(Settings).one_or_none()
        self.email_from = self.settings.mail_from

    @property
    @abstractmethod
    def message(self) -> MIMEBase:  # pragma: no cover
        pass

    def send(self):
        user = self.settings.smtp_user
        password = self.settings.smtp_pass

        if self.settings.ssl_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port, context=context) as server:
                if user is not None:
                    server.login(user, password)
                server.sendmail(self.email_from, self.email_to, self.message.as_string())

        else:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                if self.settings.starttls:
                    server.starttls()
                if user is not None:
                    server.login(user, password)
                server.sendmail(self.email_from, self.email_to, self.message.as_string())


class EmailXssNotification(EmailNotification):
    xss: XSS

    def __init__(self, xss: XSS) -> None:
        super().__init__()
        self.xss = xss
        self.email_to = self.xss.client.mail_to or self.settings.mail_to

    @property
    def message(self) -> MIMEMultipart:
        j2_environment = Environment(loader=FileSystemLoader("app/templates"))
        email_template = j2_environment.get_template("email_notification.html")

        text_content = f"XSS Catcher just caught a new {self.xss.xss_type} XSS for client {self.xss.client.name}"
        html_content = email_template.render(
            client_name=self.xss.client.name,
            xss_type=self.xss.xss_type,
            timestamp=datetime.fromtimestamp(self.xss.timestamp),
            ip_address=self.xss.ip_addr,
            tags=", ".join(json.loads(self.xss.tags)),
            nb_data=len(json.loads(self.xss.data)),
        )
        message = MIMEMultipart("alternative")
        message["To"] = self.email_to
        message["From"] = f"XSS Catcher <{self.email_from}>"
        message["Subject"] = f"Captured {self.xss.xss_type} XSS for client {self.xss.client.name}"
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


class WebhookNotification(Notification, metaclass=ABCMeta):
    settings: Settings
    webhook_type: int
    webhook_url: str

    def __init__(self) -> None:
        self.settings: Settings = db.session.query(Settings).one_or_none()
        self.webhook_type = self.settings.webhook_type

    @property
    def message(self) -> Dict[str, Any]:
        if self.webhook_type == WebhookType.DISCORD.value:
            return self.discord_message
        else:
            return self.slack_message

    @property
    @abstractmethod
    def slack_message(self) -> Dict[str, Any]:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def discord_message(self) -> Dict[str, Any]:  # pragma: no cover
        pass

    def send(self):
        requests.post(url=self.webhook_url, json=self.message)


class WebhookXssNotification(WebhookNotification):
    xss: XSS

    def __init__(self, xss: XSS) -> None:
        super().__init__()
        self.xss = xss
        self.webhook_url = xss.client.webhook_url or self.settings.webhook_url

    @property
    def slack_message(self) -> Dict[str, Any]:
        return {
            "text": f"XSS Catcher just caught a new {self.xss.xss_type} XSS for client {self.xss.client.name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*XSS Catcher just caught a new XSS*",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f":bust_in_silhouette: *Client:* {self.xss.client.name}"},
                        {"type": "mrkdwn", "text": f":lock: *XSS type:* {self.xss.xss_type}"},
                        {"type": "mrkdwn", "text": f":calendar: *Timestamp:* {datetime.fromtimestamp(self.xss.timestamp)}"},
                        {"type": "mrkdwn", "text": f":globe_with_meridians: *IP address:* {self.xss.ip_addr}"},
                        {"type": "mrkdwn", "text": f":label: *Tags:* {', '.join(json.loads(self.xss.tags)) or '_None_'}"},
                        {"type": "mrkdwn", "text": f":floppy_disk: *Data collected:* {len(json.loads(self.xss.data))}"},
                    ],
                },
                {"type": "divider"},
            ],
        }

    @property
    def discord_message(self) -> Dict[str, Any]:
        return {
            "content": f"**XSS Catcher just caught a new XSS**",
            "embeds": [
                {
                    "fields": [
                        {"inline": True, "name": ":bust_in_silhouette: **Client**", "value": self.xss.client.name},
                        {"inline": True, "name": ":lock: **XSS type**", "value": self.xss.xss_type},
                        {"inline": True, "name": ":calendar: **Timestamp**", "value": str(datetime.fromtimestamp(self.xss.timestamp))},
                        {"inline": True, "name": ":globe_with_meridians: **IP address**", "value": self.xss.ip_addr},
                        {"inline": True, "name": ":label: **Tags**", "value": ", ".join(json.loads(self.xss.tags)) or "*None*"},
                        {"inline": True, "name": ":floppy_disk: **Data collected**", "value": len(json.loads(self.xss.data))},
                    ],
                }
            ],
        }


class WebhookTestNotification(WebhookNotification):
    def __init__(self, webhook_url: str) -> None:
        super().__init__()
        self.webhook_url = webhook_url

    @property
    def slack_message(self) -> Dict[str, str]:
        return {"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}

    @property
    def discord_message(self) -> Dict[str, str]:
        return {"content": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}
