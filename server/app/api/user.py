import base64
import io

import pyotp
import pyqrcode
from app import db
from app.api.models import (
    UNDEFINED,
    ChangePasswordModel,
    RegisterModel,
    SetMfaModel,
    UserPatchModel,
)
from app.permissions import (
    Permission,
    authorization_required,
    get_current_user,
    permissions,
)
from app.schemas import ApiKey, User
from flask import Blueprint
from flask_pydantic import validate

user_bp = Blueprint("users", __name__, url_prefix="/api/user")


@user_bp.route("", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def register(body: RegisterModel):
    if db.session.execute(db.select(User).filter_by(username=body.username)).scalar_one_or_none() is not None:
        return {"msg": "This user already exists"}, 400

    user = User(username=body.username, first_login=True, is_admin=False)
    password = user.generate_password()
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return {"password": password}


@user_bp.route("/password", methods=["POST"])
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


@user_bp.route("/<int:user_id>/password", methods=["POST"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
def reset_password(user_id: int):
    user: User = db.first_or_404(db.select(User).filter_by(id=user_id))

    password = user.generate_password()
    user.set_password(password)
    user.first_login = True

    db.session.commit()
    return {"password": password}


@user_bp.route("/current", methods=["GET"])
@authorization_required()
def get_user():
    current_user: User = get_current_user()

    return current_user.to_dict()


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
def delete_user(user_id: int):
    current_user: User = get_current_user()

    user_count = db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
    if user_count is not None and user_count <= 1:
        return {"msg": "Can't delete the only user"}, 400

    if current_user.id == user_id:
        return {"msg": "Can't delete yourself"}, 400

    user: User = db.first_or_404(db.select(User).filter_by(id=user_id))

    db.session.delete(user)
    db.session.commit()

    return {"msg": f"User {user.username} deleted successfully"}


@user_bp.route("/<int:user_id>", methods=["PATCH"])
@authorization_required()
@permissions(all_of={Permission.ADMIN})
@validate()
def edit_user(user_id: int, body: UserPatchModel):
    current_user: User = get_current_user()

    if current_user.id == user_id:
        return {"msg": "Can't demote yourself"}, 400

    user: User = db.first_or_404(db.select(User).filter_by(id=user_id))

    if body.is_admin is not UNDEFINED and isinstance(body.is_admin, bool):
        user.is_admin = body.is_admin

    db.session.commit()

    return {"msg": f"User {user.username} modified successfully"}


@user_bp.route("", methods=["GET"])
@authorization_required()
def get_all_users():
    users: list[User] = list(db.session.execute(db.select(User)).scalars().all())

    return [user.to_dict() for user in users]


@user_bp.route("/mfa", methods=["GET"])
@authorization_required()
def get_mfa():
    current_user: User = get_current_user()

    secret = pyotp.random_base32()
    secret_provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.username, issuer_name="XSS Catcher")

    qr_code = pyqrcode.create(secret_provisioning_uri)
    in_memory_image = io.BytesIO()
    qr_code.png(in_memory_image, scale=3, module_color="#9cdcfe", background="#1f1f1f")
    base64_qr_code = base64.b64encode(in_memory_image.getvalue()).decode("ascii")

    return {"secret": secret, "qr_code": base64_qr_code}


@user_bp.route("/mfa", methods=["POST"])
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


@user_bp.route("/<int:user_id>/mfa", methods=["DELETE"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def delete_mfa(user_id: int):
    user: User = db.first_or_404(db.select(User).filter_by(id=user_id))

    user.mfa_secret = None

    db.session.commit()

    return {"msg": f"MFA removed for user {user.username}"}


@user_bp.route("/apikey", methods=["POST"])
@authorization_required()
def create_api_key():
    current_user: User = get_current_user()

    api_key_count = db.session.execute(db.select(db.func.count()).select_from(ApiKey).where(ApiKey.owner_id == current_user.id)).scalar()
    if api_key_count is not None and api_key_count >= 5:
        return {"msg": "You already have 5 API keys"}, 400

    api_key = ApiKey(owner_id=current_user.id, key=ApiKey.generate_key())
    db.session.add(api_key)
    db.session.commit()

    return api_key.to_dict()


@user_bp.route("/apikey/<int:key_id>", methods=["DELETE"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def delete_api_key(key_id: int):
    api_key: ApiKey = db.first_or_404(db.select(ApiKey).filter_by(id=key_id))

    db.session.delete(api_key)
    db.session.commit()

    return {"msg": "API key deleted successfully"}


@user_bp.route("/<int:user_id>/apikey", methods=["GET"])
@authorization_required()
@permissions(any_of={Permission.ADMIN, Permission.OWNER})
def list_api_keys(user_id: int):
    api_keys: list[ApiKey] = list(db.session.execute(db.select(ApiKey).filter_by(owner_id=user_id)).scalars().all())

    return [api_key.to_obfuscated_dict() for api_key in api_keys]
