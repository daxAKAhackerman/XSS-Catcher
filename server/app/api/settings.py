from app import db
from app.api import bp
from app.api.models import SettingsPatchModel
from app.decorators import permissions
from app.models import Settings
from app.utils import send_mail, send_webhook
from app.validators import check_length, is_email
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate


@bp.route("/settings", methods=["GET"])
@jwt_required()
@permissions(all_of=["admin"])
def settings_get():
    settings: Settings = db.session.query(Settings).first()

    return settings.to_dict()


@bp.route("/settings", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
@validate()
def settings_patch(body: SettingsPatchModel):
    settings: Settings = db.session.query(Settings).first()

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
        return {"msg": "Missing SMTP port"}, 400

    if settings.starttls and settings.ssl_tls:
        return {"msg": "Cannot use STARTTLS and SSL/TLS at the same time"}, 400

    if settings.smtp_host and not settings.mail_from:
        return {"msg": "Missing sender address"}, 400

    db.session.commit()

    return {"msg": "Configuration saved successfuly"}


@bp.route("/settings/smtp_test", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def smtp_test_post():
    data = request.get_json()

    settings = Settings.query.first()

    if "mail_to" not in data.keys():
        return jsonify({"status": "error", "detail": "Missing recipient"}), 400

    if is_email(data["mail_to"]) and check_length(data["mail_to"], 256):

        try:
            send_mail(receiver=data["mail_to"])
            settings.smtp_status = True
            db.session.commit()
            return jsonify({"status": "OK", "detail": "SMTP configuration test successful"}), 200
        except:
            settings.smtp_status = False
            db.session.commit()
            return (
                jsonify(
                    {
                        "status": "error",
                        "detail": "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it. ",
                    }
                ),
                400,
            )
    else:
        return jsonify({"status": "error", "detail": "Invalid recipient"}), 400


@bp.route("/settings/webhook_test", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def webhook_test_post():
    data = request.get_json()

    if "webhook_url" not in data.keys():
        return jsonify({"status": "error", "detail": "Missing webhook url"}), 400

    try:
        send_webhook(receiver=data["webhook_url"])
        return jsonify({"status": "OK", "detail": "Webhook configuration test successful"}), 200
    except:
        return jsonify({"status": "error", "detail": "Could not send test webhook"}), 400
