import logging

from app import db
from app.api.models import (
    UNDEFINED,
    EditSettingsModel,
    TestSmtpSettingsModel,
    TestWebhookSettingsModel,
)
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
def get_settings():
    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    return settings.to_dict()


@settings_bp.route("", methods=["PATCH"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def edit_settings(body: EditSettingsModel):
    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    for k in body.model_dump().keys():
        if body.__getattribute__(k) is not UNDEFINED:
            settings.__setattr__(k, body.__getattribute__(k))

    if settings.smtp_host is None:
        for k in {
            "smtp_port",
            "starttls",
            "ssl_tls",
            "mail_from",
            "mail_to",
            "smtp_user",
            "smtp_pass",
            "smtp_status",
        }:
            settings.__setattr__(k, None)

    if settings.smtp_user is None:
        settings.smtp_pass = None

    if settings.smtp_host and settings.smtp_port is None:
        db.session.rollback()
        return {"msg": "Missing SMTP port"}, 400

    if settings.smtp_host and settings.mail_from is None:
        db.session.rollback()
        return {"msg": "Missing sender address"}, 400

    if settings.starttls is True and settings.ssl_tls is True:
        db.session.rollback()
        return {"msg": "Cannot use STARTTLS and SSL/TLS at the same time"}, 400

    db.session.commit()

    return {"msg": "Configuration saved successfully"}


@settings_bp.route("/smtp_test", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def test_smtp_settings(body: TestSmtpSettingsModel):
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
        return {"msg": "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it"}, 400


@settings_bp.route("/webhook_test", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def test_webhook_settings(body: TestWebhookSettingsModel):
    try:
        WebhookTestNotification(webhook_url=body.webhook_url).send()
        return {"msg": "Webhook configuration test successful"}
    except Exception as e:
        logger.error(e)
        return {"msg": "Could not send test webhook"}, 400
