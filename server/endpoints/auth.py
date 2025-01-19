import pyotp
import sqlalchemy
from authentication import TokenType, UserSession, create_token, validate_token
from database import DbSession
from fastapi import APIRouter, HTTPException
from models.auth import (
    BlockedJti,
    Login,
    LoginResponse,
    RefreshToken,
    RefreshTokenResponse,
)
from models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(body: Login, db_session: DbSession):
    user = User.get_user_by_username(db_session, body.username)

    if not user or not user.check_password(body.password):
        raise HTTPException(401, "Bad username or password")

    if user.mfa_secret:
        if not body.otp:
            raise HTTPException(401, "OTP is required")
        elif not pyotp.TOTP(user.mfa_secret).verify(body.otp):
            raise HTTPException(401, "Bad OTP")

    refresh_token, refresh_token_id = create_token(user.get_id(), TokenType.REFRESH)
    access_token, access_token_id = create_token(user.get_id(), TokenType.ACCESS, refresh_token_id)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(body: RefreshToken, db_session: DbSession):
    user, token_payload = validate_token(db_session, body.refresh_token, TokenType.REFRESH)
    refresh_token, refresh_token_id = create_token(user.get_id(), TokenType.REFRESH)

    return {"refresh_token": refresh_token}


@router.post("/logout")
def logout(user_session: UserSession, db_session: DbSession):
    user, token_payload = user_session

    blocked_jti = BlockedJti.model_validate({"jti": token_payload["refresh_token_id"]})
    db_session.add(blocked_jti)
    try:
        db_session.commit()
    except sqlalchemy.exc.IntegrityError:
        pass
