from typing import List

from app import db
from app.api.models import ClientPatchModel, ClientPostModel
from app.models import XSS, Client, User
from app.permissions import authorization_required, get_current_user, permissions
from flask import Blueprint
from flask_pydantic import validate

client_bp = Blueprint("client", __name__, url_prefix="/api/client")


@client_bp.route("", methods=["POST"])
@authorization_required()
@validate()
def client_post(body: ClientPostModel):
    current_user: User = get_current_user()

    if db.session.query(Client).filter_by(name=body.name).count() > 0:
        return {"msg": "Client already exists"}, 400

    new_client = Client(name=body.name, description=body.description, owner_id=current_user.id)
    new_client.generate_uid()
    db.session.add(new_client)
    db.session.commit()
    return {"msg": f"New client {new_client.name} created successfully"}, 201


@client_bp.route("/<int:client_id>", methods=["GET"])
@authorization_required()
def client_get(client_id: int):
    client: Client = db.session.query(Client).filter_by(id=client_id).first_or_404()

    return client.to_dict()


@client_bp.route("/<int:client_id>", methods=["PATCH"])
@authorization_required()
@permissions(one_of=["admin", "owner"])
@validate()
def client_patch(client_id: int, body: ClientPatchModel):
    client: Client = db.session.query(Client).filter_by(id=client_id).first_or_404()

    if body.name is not None:
        if body.name != client.name and db.session.query(Client).filter_by(name=body.name).one_or_none() is not None:
            db.session.remove()
            return {"msg": "Another client already uses this name"}, 400
        client.name = body.name

    if body.description is not None:
        client.description = body.description

    if body.owner is not None:
        if db.session.query(User).filter_by(id=body.owner).one_or_none() is None:
            db.session.remove()
            return {"msg": "This user does not exist"}, 400
        client.owner_id = body.owner

    if body.mail_to is not None:
        if body.mail_to == "":
            client.mail_to = None
        else:
            client.mail_to = body.mail_to

    if body.webhook_url is not None:
        if body.webhook_url == "":
            client.webhook_url = None
        else:
            client.webhook_url = body.webhook_url

    db.session.commit()

    return {"msg": f"Client {client.name} edited successfully"}


@client_bp.route("/<int:client_id>", methods=["DELETE"])
@authorization_required()
@permissions(one_of=["admin", "owner"])
def client_delete(client_id: int):
    client: Client = db.session.query(Client).filter_by(id=client_id).first_or_404()
    db.session.query(XSS).filter_by(client_id=client_id).delete()
    db.session.delete(client)
    db.session.commit()

    return {"msg": f"Client {client.name} deleted successfully"}


@client_bp.route("", methods=["GET"])
@authorization_required()
def client_get_all():
    clients: List[Client] = db.session.query(Client).order_by(Client.id.desc()).all()
    return [client.summary() for client in clients]
