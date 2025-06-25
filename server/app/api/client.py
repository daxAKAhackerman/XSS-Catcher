from typing import List

from app import db
from app.api.models import ClientPatchModel, ClientPostModel
from app.permissions import (
    Permission,
    authorization_required,
    get_current_user,
    permissions,
)
from app.schemas import XSS, Client, User
from flask import Blueprint
from flask_pydantic import validate

client_bp = Blueprint("client", __name__, url_prefix="/api/client")


@client_bp.route("", methods=["POST"])
@authorization_required()
@validate()
def client_post(body: ClientPostModel):
    current_user: User = get_current_user()

    client_count = db.session.execute(db.select(db.func.count()).select_from(Client).where(Client.name == body.name)).scalar()
    if client_count is not None and client_count > 0:
        return {"msg": "Client already exists"}, 400

    new_client = Client(name=body.name, description=body.description, owner_id=current_user.id)
    new_client.set_uid()
    db.session.add(new_client)
    db.session.commit()
    return {"msg": f"New client {new_client.name} created successfully"}, 201


@client_bp.route("/<int:client_id>", methods=["GET"])
@authorization_required()
def client_get(client_id: int):
    client: Client = db.first_or_404(db.select(Client).filter_by(id=client_id))

    return client.to_dict()


@client_bp.route("/<int:client_id>", methods=["PATCH"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
@validate()
def client_patch(client_id: int, body: ClientPatchModel):
    client: Client = db.first_or_404(db.select(Client).filter_by(id=client_id))

    if body.name is not None:
        if body.name != client.name and db.session.execute(db.select(Client).filter_by(name=body.name)).scalar_one_or_none() is not None:
            db.session.remove()
            return {"msg": "Another client already uses this name"}, 400
        client.name = body.name

    if body.description is not None:
        client.description = body.description

    if body.owner is not None:
        if db.session.execute(db.select(User).filter_by(id=body.owner)).scalar_one_or_none() is None:
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
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def client_delete(client_id: int):
    client: Client = db.first_or_404(db.select(Client).filter_by(id=client_id))
    db.session.execute(db.delete(XSS).where(XSS.client_id == client_id))
    db.session.delete(client)
    db.session.commit()

    return {"msg": f"Client {client.name} deleted successfully"}


@client_bp.route("", methods=["GET"])
@authorization_required()
def client_get_all():
    clients: List[Client] = list(db.session.execute(db.select(Client).order_by(Client.id.desc())).scalars().all())
    return [client.summary() for client in clients]
