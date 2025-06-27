from typing import Optional

import pyotp
from app import db
from app.api.models import LoginModel
from app.permissions import authorization_required, get_current_user
from app.schemas import BlockedJti, User
from flask import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from flask_pydantic import validate

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
@authorization_required(optional=True)
@validate()
def login(body: LoginModel):
    current_user = get_current_user()

    if current_user:
        return {"msg": "Already logged in"}, 400

    user: Optional[User] = db.session.execute(db.select(User).filter_by(username=body.username)).scalar_one_or_none()
    if user is None or not user.check_password(body.password):
        return {"msg": "Bad username or password"}, 403

    if user.mfa_secret:
        if not body.otp:
            return {"msg": "OTP is required"}
        elif not pyotp.TOTP(user.mfa_secret).verify(body.otp):
            return {"msg": "Bad OTP"}, 400

    return {"access_token": create_access_token(user.username), "refresh_token": create_refresh_token(user.username)}


@auth_bp.route("/refresh", methods=["POST"])
@authorization_required(refresh=True)
def refresh_token():
    current_user: User = get_current_user()
    return {"access_token": create_access_token(identity=current_user.username)}


@auth_bp.route("/logout", methods=["POST"])
@authorization_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    blocked_jti = BlockedJti(jti=jti)
    db.session.add(blocked_jti)
    db.session.commit()
    return {"msg": "Logged out successfully"}
