import json
import logging
import time
from typing import Optional

from app import db
from app.notifications import EmailXssNotification, WebhookXssNotification
from app.schemas import XSS, Client, Settings
from flask import Blueprint, request
from flask_cors import cross_origin

logger = logging.getLogger()
logger.setLevel(logging.INFO)

x_bp = Blueprint("x", __name__, url_prefix="/api/x")


@x_bp.route("/<flavor>/<uid>", methods=["GET", "POST"])
@cross_origin()
def catch_xss(flavor: str, uid: str):
    client: Optional[Client] = db.session.execute(db.select(Client).filter_by(uid=uid)).scalar_one_or_none()

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
        if value not in ["", "{}", "[]"]:
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

    settings: Settings = db.session.execute(db.select(Settings)).scalar_one()

    if settings.smtp_host is not None and (settings.mail_to is not None or xss.client.mail_to is not None):
        try:
            EmailXssNotification(xss=xss).send()
            settings.smtp_status = True
            db.session.commit()
        except Exception as e:
            logger.error(e)
            settings.smtp_status = False
            db.session.commit()

    if settings.webhook_url is not None or xss.client.webhook_url is not None:
        try:
            WebhookXssNotification(xss=xss).send()
        except Exception as e:
            logger.error(e)

    return {"msg": "OK"}
