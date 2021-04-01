import smtplib
import ssl
from email.mime.text import MIMEText

import requests
from app.models import Settings


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
