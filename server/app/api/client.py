from app import db
from app.api import bp
from app.api.models import ClientPostModel
from app.decorators import permissions
from app.models import XSS, Client, User
from app.validators import check_length, is_email, is_url, not_empty
from flask import jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from flask_pydantic import validate


@bp.route("/client", methods=["POST"])
@jwt_required()
@validate()
def client_post(body: ClientPostModel):
    current_user: User = get_current_user()

    if db.session.query(Client).filter_by(name=body.name).count() > 0:
        return {"msg": "Client already exists"}, 400

    new_client = Client(name=body.name, description=body.description, owner_id=current_user.id)
    new_client.gen_uid()
    db.session.add(new_client)
    db.session.commit()
    return {"msg": f"New client {new_client.name} created successfuly"}, 201


@bp.route("/client/<int:client_id>", methods=["GET"])
@jwt_required()
def client_get(client_id):
    client: Client = db.session.query(Client).filter_by(id=client_id).first_or_404()

    return client.to_dict_client()


@bp.route("/client/<int:client_id>", methods=["PATCH"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def client_patch(client_id):
    """Edits a client"""
    data = request.get_json()

    client = Client.query.filter_by(id=client_id).first_or_404()

    if "name" in data.keys():

        if client.name != data["name"]:
            if Client.query.filter_by(name=data["name"]).first() != None:
                return jsonify({"status": "error", "detail": "Another client already uses this name"}), 400

        if not_empty(data["name"]) and check_length(data["name"], 32):
            client.name = data["name"]
        else:
            return jsonify({"status": "error", "detail": "Invalid name (too long or empty)"}), 400

    if "description" in data.keys():

        if check_length(data["description"], 128):
            client.description = data["description"]
        else:
            return jsonify({"status": "error", "detail": "Invalid description (too long)"}), 400

    if "owner" in data.keys():

        user = User.query.filter_by(id=data["owner"]).first()
        if user == None:
            return jsonify({"status": "error", "detail": "This user does not exist"}), 400
        client.owner_id = data["owner"]

    if "mail_to" in data.keys():

        if data["mail_to"] == "":
            client.mail_to = None
        else:
            if is_email(data["mail_to"]) and check_length(data["mail_to"], 256):
                client.mail_to = data["mail_to"]
            else:
                return jsonify({"status": "error", "detail": "Invalid mail recipient"}), 400
    else:
        client.mail_to = None

    if "webhook_url" in data.keys():
        if is_url(data["webhook_url"]):
            client.webhook_url = data["webhook_url"]
        else:
            return jsonify({"status": "error", "detail": "Webhook URL format is invalid"}), 400
    else:
        client.webhook_url = None

    db.session.commit()

    return jsonify({"status": "OK", "detail": "Client {} edited successfuly".format(client.name)}), 200


@bp.route("/client/<int:client_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def client_delete(client_id):
    """Deletes a client"""
    client = Client.query.filter_by(id=client_id).first_or_404()

    XSS.query.filter_by(client_id=client_id).delete()

    db.session.delete(client)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "Client {} deleted successfuly".format(client.name)}), 200


@bp.route("/client", methods=["GET"])
@jwt_required()
def client_all_get():
    """Gets all clients"""
    client_list = []

    clients = Client.query.order_by(Client.id.desc()).all()

    for client in clients:
        client_list.append(client.to_dict_clients())

    return jsonify(client_list), 200
