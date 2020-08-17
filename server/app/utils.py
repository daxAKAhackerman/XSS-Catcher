import smtplib
import ssl
from email.mime.text import MIMEText
from app.models import Settings


def send_mail(xss):

    settings = Settings.query.first()

    sender = settings.mail_from
    receiver = xss.client.mail_to

    msg = MIMEText('XSS Catcher just caught a new {} XSS for client {}! Go check it out!'.format(
        xss.xss_type, xss.client.name))

    msg['Subject'] = 'Captured XSS for client {}'.format(xss.client.name)
    msg['From'] = 'XSS Catcher <{}>'.format(settings.mail_from)
    msg['To'] = xss.client.mail_to

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
