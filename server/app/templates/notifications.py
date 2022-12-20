import json
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from app.models import XSS
from jinja2 import Environment, FileSystemLoader

j2_environment = Environment(loader=FileSystemLoader("app/templates"))
email_template = j2_environment.get_template("email_notification.html")


@dataclass
class TestNotification:
    @property
    def email(self) -> MIMEText:
        message = MIMEText("This is a test email from XSS catcher. If you are getting this, it's because your SMTP configuration works.")
        message["Subject"] = "XSS Catcher test mail"
        return message

    @property
    def slack(self) -> Dict[str, str]:
        return {"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}


@dataclass
class Notification:
    xss: XSS

    @property
    def email(self) -> MIMEMultipart:
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
        message["Subject"] = f"Captured {self.xss.xss_type} XSS for client {self.xss.client.name}"
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        return message

    @property
    def slack(self) -> Dict[str, Any]:
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
                        {"type": "mrkdwn", "text": f":label: *Tags:* {', '.join(json.loads(self.xss.tags))}"},
                        {"type": "mrkdwn", "text": f":floppy_disk: *Data collected:* {len(json.loads(self.xss.data))}"},
                    ],
                },
                {"type": "divider"},
            ],
        }
