import base64
import io
from typing import List

import pyotp
import pyqrcode
from app import db
from app.api import bp
from app.api.models import (
    ChangePasswordModel,
    RegisterModel,
    SetMfaModel,
    UserPatchModel,
)
from app.models import User
from app.permissions import permissions
from flask_jwt_extended import get_current_user, jwt_required
from flask_pydantic import validate


@bp.route("/user", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
@validate()
def register(body: RegisterModel):
    if db.session.query(User).filter_by(username=body.username).one_or_none() is not None:
        return {"msg": "This user already exists"}, 400

    user = User(username=body.username, first_login=True, is_admin=False)
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
    return {"msg": "Password changed successfully"}


@bp.route("/user/<int:user_id>/password", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def reset_password(user_id: int):
    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    password = user.generate_password()
    user.set_password(password)
    user.first_login = True

    db.session.commit()
    return {"password": password}


@bp.route("/user/current", methods=["GET"])
@jwt_required()
def user_get():
    current_user: User = get_current_user()

    return current_user.to_dict()


@bp.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@permissions(all_of=["admin"])
def user_delete(user_id: int):
    current_user: User = get_current_user()

    if db.session.query(User).count() <= 1:
        return {"msg": "Can't delete the only user"}, 400

    if current_user.id == user_id:
        return {"msg": "Can't delete yourself"}, 400

    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    db.session.delete(user)
    db.session.commit()

    return {"msg": f"User {user.username} deleted successfully"}


@bp.route("/user/<int:user_id>", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
@validate()
def user_patch(user_id: int, body: UserPatchModel):
    current_user: User = get_current_user()

    if current_user.id == user_id:
        return {"msg": "Can't demote yourself"}, 400

    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    user.is_admin = body.is_admin
    db.session.commit()

    return {"msg": f"User {user.username} modified successfully"}


@bp.route("/user", methods=["GET"])
@jwt_required()
def user_get_all():
    users: List[User] = db.session.query(User).all()

    return [user.to_dict() for user in users]


@bp.route("/user/mfa", methods=["GET"])
@jwt_required()
def get_mfa():
    current_user: User = get_current_user()

    secret = pyotp.random_base32()
    secret_provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.username, issuer_name="XSS Catcher")

    qr_code = pyqrcode.create(secret_provisioning_uri)
    in_memory_image = io.BytesIO()
    qr_code.png(in_memory_image, scale=3)
    base64_qr_code = base64.b64encode(in_memory_image.getvalue()).decode("ascii")

    return {"secret": secret, "qr_code": base64_qr_code}


@bp.route("/user/mfa", methods=["POST"])
@jwt_required()
@validate()
def set_mfa(body: SetMfaModel):
    totp = pyotp.TOTP(body.secret)
    if not totp.verify(body.otp):
        return {"msg": "Bad OTP"}, 400

    current_user: User = get_current_user()
    current_user.mfa_secret = body.secret
    db.session.commit()

    return {"msg": "MFA set successfully"}


@bp.route("/user/<int:user_id>/mfa", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def delete_mfa(user_id: int):
    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    user.mfa_secret = None

    db.session.commit()

    return {"msg": f"MFA removed for user {user.username}"}
