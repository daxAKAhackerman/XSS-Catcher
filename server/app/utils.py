import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from functools import wraps
from typing import Callable, Dict, List

import requests
from app import db
from app.models import XSS, Client, Settings, User
from flask_jwt_extended import get_current_user

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_xss_mail(xss: XSS):
    settings: Settings = db.session.query(Settings).first()
    mail_from = settings.mail_from
    mail_to = xss.client.mail_to or settings.mail_to

    message = MIMEText(f"XSS Catcher just caught a new {xss.xss_type} XSS for client {xss.client.name}! Go check it out!")
    message["Subject"] = f"Captured XSS for client {xss.client.name}"
    message["To"] = mail_to
    message["From"] = f"XSS Catcher <{mail_from}>"
    _send_mail(settings, mail_from, mail_to, message)


def send_test_mail(mail_to: str):
    settings: Settings = db.session.query(Settings).first()
    mail_from = settings.mail_from

    message = MIMEText("This is a test email from XSS catcher. If you are getting this, it's because your SMTP configuration works.")
    message["Subject"] = "XSS Catcher mail test"
    message["To"] = mail_to
    message["From"] = f"XSS Catcher <{mail_from}>"
    _send_mail(settings, mail_from, mail_to, message)


def _send_mail(settings: Settings, mail_from: str, mail_to: str, message: MIMEText):
    user = settings.smtp_user
    password = settings.smtp_pass

    if settings.ssl_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
            if user is not None:
                server.login(user, password)
            server.sendmail(mail_from, mail_to, message.as_string())

    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.starttls:
                server.starttls()
            if user is not None:
                server.login(user, password)
            server.sendmail(mail_from, mail_to, message.as_string())


def send_xss_webhook(xss: XSS):
    settings: Settings = db.session.query(Settings).first()
    webhook_url = xss.client.webhook_url or settings.webhook_url

    message = {"text": f"XSS Catcher just caught a new {xss.xss_type} XSS for client {xss.client.name}! Go check it out!"}

    _send_webhook(webhook_url, message)


def send_test_webhook(webhook_url: str):
    message = {"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}

    _send_webhook(webhook_url, message)


def _send_webhook(webhook_url: str, message: Dict[str, str]):
    requests.post(url=webhook_url, json=message)


def permissions(all_of: List[str] = [], one_of: List[str] = []):
    def decorator(original_function: Callable):
        @wraps(original_function)
        def new_function(*args, **kwargs):
            current_user: User = get_current_user()

            permission_attributes = [current_user.is_admin]

            if "client_id" in kwargs:
                client: Client = db.session.query(Client).filter_by(id=kwargs["client_id"]).first_or_404()
                permission_attributes.append(current_user.id == client.owner_id)
            elif "xss_id" in kwargs:
                xss: XSS = db.session.query(XSS).filter_by(id=kwargs["xss_id"]).first_or_404()
                permission_attributes.append(current_user.id == xss.client.owner_id)

            if (all_of and all(permission_attributes)) or (one_of and any(permission_attributes)) or (not all_of and not one_of):
                return original_function(*args, **kwargs)

            return {"msg": "Forbidden"}, 403

        return new_function

    return decorator
