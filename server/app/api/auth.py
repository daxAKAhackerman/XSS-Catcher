from app.api import bp
from app.models import User
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_current_user


@bp.route("/auth/login", methods=["POST"])
def login():
    """Logs a user in"""
    current_user = get_current_user()

    if current_user:
        return jsonify({"status": "error", "detail": "Already logged in"}), 400
    data = request.get_json()

    if "username" not in data.keys() or "password" not in data.keys():
        return jsonify({"status": "error", "detail": "Missing username or password"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"status": "error", "detail": "Bad username or password"}), 403

    return jsonify({"status": "OK", "detail": {"access_token": create_access_token(user.username)}}), 200
