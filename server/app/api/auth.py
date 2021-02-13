from app import db
from app.api import bp
from app.models import Blacklist, User
from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_current_user, get_raw_jwt, jwt_refresh_token_required


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

    return jsonify({"status": "OK", "detail": {"access_token": create_access_token(user.username), "refresh_token": create_refresh_token(user.username)}}), 200


@bp.route("/auth/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    """Uses a refresh token to generate a new access token"""
    current_user = get_current_user()
    return jsonify({"status": "OK", "detail": {"access_token": create_access_token(identity=current_user.username)}}), 200


@bp.route("/auth/logout", methods=["POST"])
@jwt_refresh_token_required
def logout():
    """Adds a refresh token jti to the blacklist"""
    jti = get_raw_jwt()["jti"]
    blacklisted_jti = Blacklist(jti=jti)
    db.session.add(blacklisted_jti)
    db.session.commit()
    return jsonify({"status": "OK", "detail": "Logged out successfully"}), 200
