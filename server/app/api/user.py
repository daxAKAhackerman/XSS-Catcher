from flask import jsonify, request
from app.api import bp
from app.models import User
from flask_login import current_user, login_required
from app.validators import is_password, not_empty, check_length
from app import db


@bp.route('/user/new', methods=['POST'])
@login_required
def register():

    data = request.form

    if 'username' not in data.keys():

        return jsonify({'status': 'error', 'detail': 'Missing username'}), 400

    if not (not_empty(data['username']) and check_length(data['username'], 128)):
        return jsonify({'status': 'error', 'detail': 'Invalid username (too long or empty)'}), 400

    if User.query.filter_by(username=data['username']).first() != None:
        return jsonify({'status': 'error', 'detail': 'This user already exists'}), 400

    user = User(username=data['username'])

    password = user.generate_password()

    user.set_password(password)

    db.session.add(user)

    db.session.commit()

    return jsonify({'status': 'OK', 'detail': password}), 200


@bp.route('/user/change_password', methods=['POST'])
@login_required
def change_password():

    data = request.form

    if ('password1' not in data.keys()) or \
       ('password2' not in data.keys()) or \
       ('old_password' not in data.keys()):
        return jsonify({'status': 'error', 'detail': 'Missing data (password1, password2 or old_password)'}), 400

    if not is_password(data['password1']):
        return jsonify({'status': 'error', 'detail': 'Password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number'}), 400

    if data['password1'] != data['password2']:
        return jsonify({'status': 'error', 'detail': 'Passwords don\'t match'}), 400

    if not current_user.check_password(data['old_password']):
        return jsonify({'status': 'error', 'detail': 'Old password is incorrect'}), 400

    current_user.set_password(data['password1'])
    current_user.first_login = False

    db.session.commit()
    return jsonify({'status': 'OK'}), 200


@bp.route('/user', methods=['GET'])
@login_required
def get_user():
    return jsonify(current_user.to_dict()), 200


@bp.route('/user/<id>', methods=['DELETE'])
@login_required
def delete_user(id):

    if len(User.query.all()) <= 1:
        return jsonify({'status': 'error', 'detail': 'Can\'t delete the only user'}), 400

    user = User.query.filter_by(id=id).first_or_404()

    db.session.delete(user)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200


@bp.route('/user/all', methods=['GET'])
@login_required
def get_users():
    users = []
    data = User.query.all()

    for user in data: 
        users.append(user.to_dict())

    return jsonify(users), 200