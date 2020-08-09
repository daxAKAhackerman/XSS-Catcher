from flask import jsonify, request
from app import db
from app.models import Client, XSS, User
from app.api import bp
from flask_login import login_required, current_user
from app.validators import not_empty, check_length
from app.decorators import permissions

import json


@bp.route('/client', methods=['PUT'])
@login_required
def client_put():
    """Creates a new client"""
    data = request.form

    if 'name' not in data.keys() or\
       'description' not in data.keys():
        return jsonify({'status': 'error', 'detail': 'Missing name or description'}), 400

    if Client.query.filter_by(name=data['name']).first() != None:
        return jsonify({'status': 'error', 'detail': 'Client already exists'}), 400

    if not_empty(data['name']) and check_length(data['name'], 32) and check_length(data['description'], 128):

        new_client = Client(
            name=data['name'], description=data['description'], owner_id=current_user.id)

        new_client.gen_uid()

        db.session.add(new_client)

        db.session.commit()
        return jsonify({'status': 'OK'}), 201
    else:
        return jsonify({'status': 'error', 'detail': 'Invalid data (name empty or too long or description too long)'}), 400


@bp.route('/client/<int:client_id>', methods=['GET'])
@login_required
def client_get(client_id):
    """Gets a client's infos"""
    client = Client.query.filter_by(id=client_id).first_or_404()

    return jsonify(client.to_dict_client()), 200


@bp.route('/client/<int:client_id>', methods=['POST'])
@login_required
@permissions(one_of=['admin', 'owner'])
def client_post(client_id):
    """Edits a client"""
    data = request.form

    client = Client.query.filter_by(id=client_id).first_or_404()

    if 'name' in data.keys():

        if client.name != data['name']:
            if Client.query.filter_by(name=data['name']).first() != None:
                return jsonify({'status': 'error', 'detail': 'Another client already uses this name'}), 400

        if not_empty(data['name']) and check_length(data['name'], 32):
            client.name = data['name']
        else:
            return jsonify({'status': 'error', 'detail': 'Invalid name (too long or empty)'}), 400

    if 'description' in data.keys():

        if check_length(data['description'], 128):
            client.description = data['description']
        else:
            return jsonify({'status': 'error', 'detail': 'Invalid description (too long)'}), 400

    if 'owner' in data.keys():
        
        user = User.query.filter_by(id=data['owner']).first()
        if user == None:
            return jsonify({'status': 'error', 'detail': 'This user does not exist'}), 400
        client.owner_id = data['owner']

    db.session.commit()

    return jsonify({'status': 'OK'}), 200


@bp.route('/client/<int:client_id>', methods=['DELETE'])
@login_required
@permissions(one_of=['admin', 'owner'])
def client_delete(client_id):
    """Deletes a client"""
    client = Client.query.filter_by(id=client_id).first_or_404()

    XSS.query.filter_by(client_id=client_id).delete()

    db.session.delete(client)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200


@bp.route('/client/<int:client_id>/<flavor>/all', methods=['GET'])
@login_required
def client_xss_all_get(client_id, flavor):
    """Gets all XSS of a particular type (reflected of stored) for a specific client"""
    if flavor != 'reflected' and flavor != 'stored':
        return jsonify({'status': 'error', 'detail': 'Unknown XSS type'}), 400

    xss_list = []
    xss = XSS.query.filter_by(
        client_id=client_id).filter_by(xss_type=flavor).all()

    for hit in xss:
        xss_list.append(hit.to_dict_short())

    return jsonify(xss_list), 200


@bp.route('/client/<int:client_id>/<int:xss_id>', methods=['GET'])
@login_required
def client_xss_get(client_id, xss_id):
    """Gets a single XSS instance for a client"""
    xss = XSS.query.filter_by(client_id=client_id).filter_by(
        id=xss_id).first_or_404()

    return jsonify(xss.to_dict()), 200


@bp.route('/client/<int:client_id>/loot', methods=['GET'])
@login_required
def client_loot_get(client_id):
    """Get all captured data for a client"""
    loot = {}

    xss = XSS.query.filter_by(client_id=client_id).all()

    for hit in xss:
        for element in json.loads(hit.data).items():
            if element[0] not in loot.keys():
                loot[element[0]] = []
            if element[0] == 'fingerprint' or element[0] == 'dom' or element[0] == 'screenshot':
                loot[element[0]].append({hit.id: ''})
            else:
                loot[element[0]].append({hit.id: element[1]})

    return jsonify(loot), 200


@bp.route('/client/all', methods=['GET'])
@login_required
def client_all_get():
    """Gets all clients"""
    client_list = []

    clients = Client.query.order_by(Client.id.desc()).all()

    for client in clients:
        client_list.append(client.to_dict_clients())

    return jsonify(client_list), 200
