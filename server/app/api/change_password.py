from flask import jsonify, request
from app.api import bp
from app.models import User
from flask_login import current_user, login_required
from app.validators import is_password
from app import db


@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():

    data = request.form

    if ('password1' not in data.keys()) or \
       ('password2' not in data.keys()) or \
       ('old_password' not in data.keys()):
        return jsonify({'status': 'error', 'detail': 'missing data'}), 400

    if not is_password(data['password1']):
        return jsonify({'status': 'error', 'detail': 'password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number'}), 400

    if data['password1'] != data['password2']:
        return jsonify({'status': 'error', 'detail': 'passwords don\'t match'}), 400

    if not current_user.check_password(data['old_password']):
        return jsonify({'status': 'error', 'detail': 'old password is incorrect'}), 403
    
    current_user.set_password(data['password1'])
    db.session.commit()
    return jsonify({'status': 'OK'})

