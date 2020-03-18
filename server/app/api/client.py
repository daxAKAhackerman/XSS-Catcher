from flask import jsonify, request
from app import db
from app.models import Client, XSS
from app.api import bp
from flask_login import login_required, current_user
from app.validators import not_empty, check_length


@bp.route('/client', methods=['PUT'])
@login_required
def create_client():
    data = request.form

    if 'name' not in data.keys() or\
       'description' not in data.keys():
        return jsonify({'status': 'error', 'detail': 'Missing name or description'}), 400

    if Client.query.filter_by(name=data['name']).first() != None:
        return jsonify({'status': 'error', 'detail': 'Client already exists'}), 400

    if not_empty(data['name']) and check_length(data['name'], 32) and check_length(data['description'], 128):

        new_client = Client(name=data['name'], description=data['description'], owner_id=current_user.id)

        new_client.gen_uid()

        db.session.add(new_client)

        db.session.commit()
        return jsonify({'status': 'OK'}), 201
    else:
        return jsonify({'status': 'error', 'detail': 'Invalid data (name empty or too long or description too long)'}), 400


@bp.route('/client/<id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def get_client(id):

    if request.method == 'GET':

        client = Client.query.filter_by(id=id).first_or_404()

        return jsonify(client.to_dict_client()), 200

    elif request.method == 'POST':

        data = request.form

        client = Client.query.filter_by(id=id).first_or_404()

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

        db.session.commit()

        return jsonify({'status': 'OK'}), 200

    elif request.method == 'DELETE':

        client = Client.query.filter_by(id=id).first_or_404()
        XSS.query.filter_by(client_id=id).delete()

        db.session.delete(client)
        db.session.commit()

        return jsonify({'status': 'OK'}), 200



@bp.route('/client/<id>/<flavor>', methods=['GET'])
@login_required
def get_client_xss(id, flavor):

    if flavor != 'reflected' and flavor != 'stored':
        return jsonify({'status': 'error', 'detail': 'Unknown XSS type'}), 400

    xss_list = []
    xss = XSS.query.filter_by(client_id=id).filter_by(xss_type=flavor).all()

    for hit in xss:
        xss_list.append(hit.to_dict())

    return jsonify(xss_list), 200


@bp.route('/client/<id>/loot', methods=['GET'])
@login_required
def get_client_loot(id):

    loot = {
        'cookies': {},
        'local_storage': {},
        'session_storage': {},
        'other_data': {}
    }

    xss = XSS.query.filter_by(client_id=id).all()

    for hit in xss:
        if hit.cookies != None:
            loot['cookies'][hit.id] = hit.cookies

        if hit.local_storage != None:
            loot['local_storage'][hit.id] = hit.local_storage

        if hit.session_storage != None:
            loot['session_storage'][hit.id] = hit.session_storage

        if hit.other_data != None: 
            loot['other_data'][hit.id] = hit.other_data

    return jsonify(loot), 200
