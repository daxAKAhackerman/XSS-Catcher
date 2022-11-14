from app import db
from app.api import bp
from app.api.models import ChangePasswordModel, RegisterModel
from app.decorators import permissions
from app.models import User
from flask import jsonify, request
from flask_jwt_extended import get_current_user, jwt_required
from flask_pydantic import validate


@bp.route("/user", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
@validate()
def register(body: RegisterModel):
    if db.session.query(User).filter_by(username=body.username).first() is not None:
        return {"msg": "This user already exists"}, 400

    user = User(username=body.username)
    password = user.generate_password()
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {"password": password}


@bp.route("/user/password", methods=["POST"])
@jwt_required()
@validate()
def change_password(body: ChangePasswordModel):
    current_user: User = get_current_user()

    if not current_user.check_password(body.old_password):
        return {"msg": "Old password is incorrect"}, 400

    current_user.set_password(body.password1)
    current_user.first_login = False

    db.session.commit()
    return {"msg": "Password changed successfuly"}


@bp.route("/user/<id>/password", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def reset_password(id):
    """Resets a user's password"""
    user = User.query.filter_by(id=id).first_or_404()

    password = user.generate_password()

    user.set_password(password)

    user.first_login = True

    db.session.commit()
    return jsonify({"status": "OK", "detail": password}), 200


@bp.route("/user/current", methods=["GET"])
@jwt_required()
def user_get():
    """Get the current user"""
    current_user = get_current_user()

    return jsonify(current_user.to_dict()), 200


@bp.route("/user/<user_id>", methods=["DELETE"])
@jwt_required()
@permissions(all_of=["admin"])
def user_delete(user_id):
    """Deletes a user"""
    current_user = get_current_user()

    if len(User.query.all()) <= 1:
        return jsonify({"status": "error", "detail": "Can't delete the only user"}), 400

    if current_user.id == int(user_id):
        return jsonify({"status": "error", "detail": "Can't delete yourself"}), 400

    user = User.query.filter_by(id=user_id).first_or_404()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "User {} deleted successfuly".format(user.username)}), 200


@bp.route("/user/<user_id>", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
def user_post(user_id):
    """Modifies a user"""
    current_user = get_current_user()

    if current_user.id == int(user_id):
        return jsonify({"status": "error", "detail": "Can't demote yourself"}), 400

    user = User.query.filter_by(id=user_id).first_or_404()

    data = request.get_json()

    if "is_admin" not in data.keys():
        return jsonify({"status": "error", "detail": "Missing data"}), 400

    if (int(data["is_admin"]) != 1) and (int(data["is_admin"]) != 0):
        return jsonify({"status": "error", "detail": "Invalid data"}), 400

    user.is_admin = int(data["is_admin"]) == 1

    db.session.commit()
    return jsonify({"status": "OK", "detail": "User {} modified successfuly".format(user.username)}), 200


@bp.route("/user", methods=["GET"])
@jwt_required()
def user_all_get():
    """Gets all users"""
    users = []
    data = User.query.all()

    for user in data:
        users.append(user.to_dict())

    return jsonify(users), 200
