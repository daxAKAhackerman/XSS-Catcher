import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from functools import wraps
from typing import Callable, List

import requests
from app import db
from app.models import XSS, Client, Settings, User
from flask_jwt_extended import get_current_user

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingDataError(Error):
    """Exception raised when data is missing."""

    def __init__(self, message):
        self.message = message


def send_mail(xss=None, receiver=None):

    settings = Settings.query.first()

    sender = settings.mail_from

    if xss:
        receiver = xss.client.mail_to if xss.client.mail_to else settings.mail_to

        msg = MIMEText("XSS Catcher just caught a new {} XSS for client {}! Go check it out!".format(xss.xss_type, xss.client.name))

        msg["Subject"] = "Captured XSS for client {}".format(xss.client.name)

        msg["To"] = xss.client.mail_to

        msg["From"] = "XSS Catcher <{}>".format(settings.mail_from)

    elif receiver:
        msg = MIMEText("This is a test email from XSS catcher. If you are getting this, it's because your SMTP configuration works. ")

        msg["Subject"] = "XSS Catcher mail test"

        msg["To"] = receiver

        msg["From"] = "XSS Catcher <{}>".format(settings.mail_from)

    else:
        raise MissingDataError("send_mail did not receive an XSS or a receiver")

    user = settings.smtp_user
    password = settings.smtp_pass

    if settings.ssl_tls:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:

            if user is not None and password is not None:
                server.login(user, password)
            server.sendmail(sender, receiver, msg.as_string())

    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:

            if user is not None and password is not None:
                server.login(user, password)

            if settings.starttls:
                server.starttls()

            server.sendmail(sender, receiver, msg.as_string())


def send_webhook(xss=None, receiver=None):

    settings = Settings.query.first()

    if xss:
        receiver = xss.client.webhook_url if xss.client.webhook_url else settings.webhook_url

        requests.post(url=receiver, json={"text": f"XSS Catcher just caught a new {xss.xss_type} XSS for client {xss.client.name}! Go check it out!"})

    elif receiver:
        requests.post(
            url=receiver, json={"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}
        )


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
