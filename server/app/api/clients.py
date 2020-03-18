from flask import jsonify
from app import db
from app.models import Client
from app.api import bp
from flask_login import login_required


@bp.route('/clients', methods=['GET'])
@login_required
def get_clients():

    client_list = []

    clients = Client.query.all()

    for client in clients:
        client_list.append(client.to_dict_clients())

    return jsonify(client_list), 200
