from flask import jsonify, request
from app.api import bp
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required

@bp.route('/auth/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'status': 'error', 'detail': 'Already logged in'}), 400
    data = request.form
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'status': 'error', 'detail': 'Bad username or password'}), 403
    login_user(user, remember=data['remember'])
    return jsonify({'status': 'OK'}), 200


@bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return  jsonify({'status': 'OK'}), 200