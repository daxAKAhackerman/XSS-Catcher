import logging

from app import db
from app.api.models import SettingsPatchModel, SmtpTestPostModel, WebhookTestPostModel
from app.notifications import EmailTestNotification, WebhookTestNotification
from app.permissions import Permission, authorization_required, permissions
from app.schemas import Settings
from flask import Blueprint
from flask_pydantic import validate

logger = logging.getLogger()
logger.setLevel(logging.INFO)

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@settings_bp.route("", methods=["GET"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
def settings_get():
    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    return settings.to_dict()


@settings_bp.route("", methods=["PATCH"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def settings_patch(body: SettingsPatchModel):
    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    if body.smtp_host is not None:
        if body.smtp_host == "":
            settings.smtp_host = None
        else:
            settings.smtp_host = body.smtp_host

    if body.mail_to is not None:
        if body.mail_to == "":
            settings.mail_to = None
        else:
            settings.mail_to = body.mail_to

    if body.smtp_user is not None:
        if body.smtp_user == "":
            settings.smtp_user = None
        else:
            settings.smtp_user = body.smtp_user

    if body.webhook_url is not None:
        if body.webhook_url == "":
            settings.webhook_url = None
        else:
            settings.webhook_url = body.webhook_url

    if body.smtp_port is not None:
        settings.smtp_port = body.smtp_port

    if body.starttls is not None:
        settings.starttls = body.starttls

    if body.ssl_tls is not None:
        settings.ssl_tls = body.ssl_tls

    if body.mail_from is not None:
        settings.mail_from = body.mail_from

    if body.smtp_pass is not None:
        settings.smtp_pass = body.smtp_pass

    if body.webhook_type is not None:
        settings.webhook_type = body.webhook_type

    if settings.smtp_host is None:
        settings.smtp_port = None
        settings.starttls = False
        settings.ssl_tls = False
        settings.mail_from = None
        settings.mail_to = None
        settings.smtp_user = None
        settings.smtp_pass = None
        settings.smtp_status = None

    if settings.smtp_user is None:
        settings.smtp_pass = None

    if settings.smtp_host and not settings.smtp_port:
        db.session.remove()
        return {"msg": "Missing SMTP port"}, 400

    if settings.smtp_host and not settings.mail_from:
        db.session.remove()
        return {"msg": "Missing sender address"}, 400

    if settings.starttls and settings.ssl_tls:
        db.session.remove()
        return {"msg": "Cannot use STARTTLS and SSL/TLS at the same time"}, 400

    db.session.commit()

    return {"msg": "Configuration saved successfully"}


@settings_bp.route("/smtp_test", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def smtp_test_post(body: SmtpTestPostModel):
    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    try:
        EmailTestNotification(email_to=body.mail_to).send()
        settings.smtp_status = True
        db.session.commit()
        return {"msg": "SMTP configuration test successful"}
    except Exception as e:
        logger.error(e)
        settings.smtp_status = False
        db.session.commit()
        return {"msg": "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it. "}, 400


@settings_bp.route("/webhook_test", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def webhook_test_post(body: WebhookTestPostModel):
    try:
        WebhookTestNotification(webhook_url=body.webhook_url).send()
        return {"msg": "Webhook configuration test successful"}
    except Exception as e:
        logger.error(e)
        return {"msg": "Could not send test webhook"}, 400
