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
from app.models import ApiKey, User
from app.permissions import authorization_required, get_current_user, permissions
from flask_pydantic import validate


@bp.route("/user", methods=["POST"])
@authorization_required()
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
@authorization_required()
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
@authorization_required()
@permissions(all_of=["admin"])
def reset_password(user_id: int):
    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    password = user.generate_password()
    user.set_password(password)
    user.first_login = True

    db.session.commit()
    return {"password": password}


@bp.route("/user/current", methods=["GET"])
@authorization_required()
def user_get():
    current_user: User = get_current_user()

    return current_user.to_dict()


@bp.route("/user/<int:user_id>", methods=["DELETE"])
@authorization_required()
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
@authorization_required()
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
@authorization_required()
def user_get_all():
    users: List[User] = db.session.query(User).all()

    return [user.to_dict() for user in users]


@bp.route("/user/mfa", methods=["GET"])
@authorization_required()
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
@authorization_required()
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
@authorization_required()
@permissions(one_of=["admin", "owner"])
def delete_mfa(user_id: int):
    user: User = db.session.query(User).filter_by(id=user_id).first_or_404()

    user.mfa_secret = None

    db.session.commit()

    return {"msg": f"MFA removed for user {user.username}"}


@bp.route("/user/apikey", methods=["POST"])
@authorization_required()
def create_api_key():
    current_user: User = get_current_user()

    if db.session.query(ApiKey).filter_by(owner_id=current_user.id).count() >= 5:
        return {"msg": "You already have 5 API keys"}, 400

    api_key = ApiKey(owner_id=current_user.id, key=ApiKey.generate_key())
    db.session.add(api_key)
    db.session.commit()

    return api_key.to_dict()


@bp.route("/user/apikey/<int:key_id>", methods=["DELETE"])
@authorization_required()
@permissions(one_of=["admin", "owner"])
def delete_api_key(key_id: int):
    api_key: ApiKey = db.session.query(ApiKey).filter_by(id=key_id).first_or_404()

    db.session.delete(api_key)
    db.session.commit()

    return {"msg": "API key deleted successfully"}


@bp.route("/user/<int:user_id>/apikey", methods=["GET"])
@authorization_required()
@permissions(one_of=["admin", "owner"])
def list_api_keys(user_id: int):
    api_keys: List[ApiKey] = db.session.query(ApiKey).filter_by(owner_id=user_id)

    return [api_key.to_obfuscated_dict() for api_key in api_keys]
