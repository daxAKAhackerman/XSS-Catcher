from app import db
from app.api import bp
from app.api.models import SettingsPatchModel
from app.decorators import permissions
from app.models import Settings
from app.utils import send_mail, send_webhook
from app.validators import check_length, is_email, is_url
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

    # if "smtp_host" in data.keys():

    #     if data["smtp_host"] != "":

    #         if check_length(data["smtp_host"], 256):
    #             settings.smtp_host = data["smtp_host"]
    #         else:
    #             return jsonify({"status": "error", "detail": "Server address too long"}), 400

    #         if "smtp_port" in data.keys():

    #             try:
    #                 smtp_port = int(data["smtp_port"])
    #             except ValueError:
    #                 return jsonify({"status": "error", "detail": "Port is invalid"}), 400

    #             if smtp_port <= 65535 and smtp_port >= 0:
    #                 settings.smtp_port = int(data["smtp_port"])
    #             else:
    #                 return jsonify({"status": "error", "detail": "Port is invalid"}), 400

    #         else:
    #             return jsonify({"status": "error", "detail": "Missing SMTP port"}), 400

    #         if "starttls" in data.keys() and "ssl_tls" in data.keys():
    #             return jsonify({"status": "error", "detail": "Cannot use STARTTLS and SSL/TLS at the same time"}), 400

    #         if "starttls" in data.keys():
    #             settings.starttls = True
    #         else:
    #             settings.starttls = False

    #         if "ssl_tls" in data.keys():
    #             settings.ssl_tls = True
    #         else:
    #             settings.ssl_tls = False

    #         if "mail_from" in data.keys():
    #             if is_email(data["mail_from"]) and check_length(data["mail_from"], 256):
    #                 settings.mail_from = data["mail_from"]
    #             else:
    #                 return jsonify({"status": "error", "detail": "Email address format is invalid"}), 400

    #         else:
    #             return jsonify({"status": "error", "detail": "Missing sender address"}), 400

    #         if "mail_to" in data.keys():
    #             if is_email(data["mail_to"]):
    #                 settings.mail_to = data["mail_to"]
    #             else:
    #                 return jsonify({"status": "error", "detail": "Recipient email address format is invalid"}), 400
    #         else:
    #             settings.mail_to = None

    #         if "smtp_user" in data.keys():

    #             if check_length(data["smtp_user"], 128):
    #                 settings.smtp_user = data["smtp_user"]
    #             else:
    #                 return jsonify({"status": "error", "detail": "SMTP username too long"}), 400

    #             if "smtp_pass" in data.keys():
    #                 if check_length(data["smtp_pass"], 128):
    #                     settings.smtp_pass = data["smtp_pass"]
    #                 else:
    #                     return jsonify({"status": "error", "detail": "SMTP password too long"}), 400

    #         else:
    #             settings.smtp_user = None
    #             settings.smtp_pass = None

    #     else:
    #         settings.smtp_host = None
    #         settings.smtp_port = None
    #         settings.starttls = False
    #         settings.ssl_tls = False
    #         settings.mail_from = None
    #         settings.mail_to = None
    #         settings.smtp_user = None
    #         settings.smtp_pass = None
    #         settings.smtp_status = None

    # else:
    #     settings.smtp_host = None
    #     settings.smtp_port = None
    #     settings.starttls = False
    #     settings.ssl_tls = False
    #     settings.mail_from = None
    #     settings.mail_to = None
    #     settings.smtp_user = None
    #     settings.smtp_pass = None
    #     settings.smtp_status = None

    if "webhook_url" in data.keys():
        if is_url(data["webhook_url"]):
            settings.webhook_url = data["webhook_url"]
        else:
            return jsonify({"status": "error", "detail": "Webhook URL format is invalid"}), 400

    else:
        settings.webhook_url = None

    db.session.commit()

    return jsonify({"status": "OK", "detail": "Configuration saved successfuly"}), 200


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
