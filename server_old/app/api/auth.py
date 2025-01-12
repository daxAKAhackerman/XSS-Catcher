import pyotp
from app import db
from app.api import bp
from app.api.models import LoginModel
from app.models import BlockedJti, User
from app.permissions import authorization_required, get_current_user
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from flask_pydantic import validate


@bp.route("/auth/login", methods=["POST"])
@authorization_required(optional=True)
@validate()
def login(body: LoginModel):
    current_user = get_current_user()

    if current_user:
        return {"msg": "Already logged in"}, 400

    user: User = db.session.query(User).filter_by(username=body.username).one_or_none()
    if user is None or not user.check_password(body.password):
        return {"msg": "Bad username or password"}, 403

    if user.mfa_secret:
        if not body.otp:
            return {"msg": "OTP is required"}
        elif not pyotp.TOTP(user.mfa_secret).verify(body.otp):
            return {"msg": "Bad OTP"}, 400

    return {"access_token": create_access_token(user.username), "refresh_token": create_refresh_token(user.username)}


@bp.route("/auth/refresh", methods=["POST"])
@authorization_required(refresh=True)
def refresh():
    current_user: User = get_current_user()
    return {"access_token": create_access_token(identity=current_user.username)}


@bp.route("/auth/logout", methods=["POST"])
@authorization_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    blocked_jti = BlockedJti(jti=jti)
    db.session.add(blocked_jti)
    db.session.commit()
    return {"msg": "Logged out successfully"}
