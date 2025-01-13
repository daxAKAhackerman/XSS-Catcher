import pyotp
from authentication import TokenType, create_token
from database import DbSession
from fastapi import APIRouter, HTTPException
from models.auth import Login
from models.user import User

router = APIRouter()


@router.post("/login")
def login(body: Login, db_session: DbSession):
    user = User.get_user_by_username(db_session, body.username)

    if not user or not user.check_password(body.password):
        raise HTTPException(401, "Bad username or password")

    if user.mfa_secret:
        if not body.otp:
            raise HTTPException(401, "OTP is required")
        elif not pyotp.TOTP(user.mfa_secret).verify(body.otp):
            raise HTTPException(401, "Bad OTP")

    return {"access_token": create_token(user.get_id(), TokenType.ACCESS), "refresh_token": create_token(user.get_id(), TokenType.REFRESH)}
