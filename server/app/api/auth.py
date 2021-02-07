from app.api import bp
from app.models import User
from flask import jsonify, request
from flask_login import current_user, login_required, login_user, logout_user


@bp.route("/auth/login", methods=["POST"])
def login():
    """Logs a user in"""
    if current_user.is_authenticated:
        return jsonify({"status": "error", "detail": "Already logged in"}), 400
    data = request.get_json()

    if "username" not in data.keys() or "password" not in data.keys():
        return jsonify({"status": "error", "detail": "Missing username or password"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"status": "error", "detail": "Bad username or password"}), 403

    if "remember" not in data.keys():
        remember = False
    else:
        remember = True

    login_user(user, remember=remember)
    return jsonify({"status": "OK", "detail": "Logged in successfuly"}), 200


@bp.route("/auth/logout", methods=["GET"])
@login_required
def logout():
    """Logs a user out"""
    logout_user()
    return jsonify({"status": "OK", "detail": "Logged out successfuly"}), 200
