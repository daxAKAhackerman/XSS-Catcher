import json
import time

from app import db
from app.api import bp
from app.models import XSS, Client, Settings
from app.utils import logger, send_mail, send_webhook
from flask import request
from flask_cors import cross_origin


@bp.route("/x/<flavor>/<uid>", methods=["GET", "POST"])
@cross_origin()
def catch_xss(flavor: str, uid: str):
    client: Client = db.session.query(Client).filter_by(uid=uid).first()

    if client is None:
        return {"msg": "OK"}

    xss_type = "reflected" if flavor == "r" else "stored"
    ip_addr = request.headers["X-Forwarded-For"].split(", ")[0] if "X-Forwarded-For" in request.headers else request.remote_addr

    if request.method == "GET":
        parameters = request.args.to_dict()
    elif request.method == "POST" and request.is_json:
        parameters = request.get_json()
    else:
        parameters = request.form

    headers = {header[0]: header[1] for header in request.headers}

    data = {}
    tags = []

    for param, value in parameters.items():
        if not value in ["", "{}", "[]"]:
            if param == "cookies":
                if "cookies" not in data.keys():
                    data["cookies"] = {}
                cookies = value.split("; ")
                for cookie in cookies:
                    cookie_name, cookie_value = cookie.split("=", 1)
                    data["cookies"].update({cookie_name: cookie_value})

            elif param == "local_storage" or param == "session_storage":
                if param not in data.keys():
                    data[param] = {}
                local_storage = json.loads(value)
                data[param].update(local_storage)

            elif param == "dom":
                data["dom"] = f"<html>\n{value}\n</html>"

            elif param == "tags":
                tags = value.split(",")

            else:
                data[param] = value

    xss = XSS(
        headers=json.dumps(headers),
        ip_addr=ip_addr,
        client_id=client.id,
        xss_type=xss_type,
        data=json.dumps(data),
        timestamp=int(time.time()),
        tags=json.dumps(tags),
    )
    db.session.add(xss)
    db.session.commit()

    settings: Settings = db.session.query(Settings).first()

    if settings.smtp_host is not None and (settings.mail_to is not None or xss.client.mail_to is not None):
        try:
            send_mail(xss=xss)
            settings.smtp_status = True
            db.session.commit()
        except Exception as e:
            logger.error(e)
            settings.smtp_status = False
            db.session.commit()

    if settings.webhook_url is not None or xss.client.webhook_url is not None:
        try:
            send_webhook(xss=xss)
        except Exception as e:
            logger.error(e)

    return {"msg": "OK"}
