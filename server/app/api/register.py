from flask import jsonify, request
from app import db
from app.models import User
from app.api import bp
from app.validators import not_empty, check_length


@bp.route('/register', methods=['POST'])
def register():

    data = request.form

    # is everything here?

    if 'username' not in data.keys():

        return jsonify({'status': 'error', 'detail': 'missing data'}), 400

    # is everything ok?

    if not (not_empty(data['username']) and check_length(data['username'], 128)):
        return jsonify({'status': 'error', 'detail': 'invalid username'}), 400

    # does it already exists?

    if User.query.filter_by(username=data['username']).first() != None:
        return jsonify({'status': 'error', 'detail': 'an error has occurred'}), 400

    user = User(username=data['username'])

    password = user.generate_password()

    user.set_password(password)

    db.session.add(user)

    db.session.commit()

    return jsonify({'status': 'OK', 'detail': password})
