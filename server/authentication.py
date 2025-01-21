import datetime
import os
import random
import string
import uuid
from enum import StrEnum
from typing import Annotated, Any, Optional

import jwt
from database import DbSession
from fastapi import Depends, HTTPException, Request
from models.auth import BlockedJti
from models.user import User

if os.getenv("DEV", "0") == "1":
    ACCESS_TOKEN_LIFETIME = 60 * 60
    JWT_SECRET = "dev_secret"
else:
    ACCESS_TOKEN_LIFETIME = 5 * 60
    JWT_SECRET = "".join(random.choice(string.ascii_letters + string.digits) for i in range(12))


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def create_token(user_id: int, token_type: TokenType, refresh_token_id: Optional[str] = None) -> tuple[str, str]:
    ts = int(datetime.datetime.now().timestamp())
    exp = ts + ACCESS_TOKEN_LIFETIME
    jti = str(uuid.uuid4())

    payload = {
        "iat": ts,
        "jti": jti,
        "type": token_type,
        "sub": str(user_id),
        "nbf": ts,
        "exp": exp,
    }

    if refresh_token_id:
        payload["refresh_token_id"] = refresh_token_id

    return jwt.encode(payload, JWT_SECRET, algorithm="HS256"), jti


class SessionValidator:
    require_admin: Optional[bool] = None

    def __init__(self, require_admin: Optional[bool] = None):
        self.require_admin = require_admin

    def __call__(self, request: Request, db_session: DbSession) -> tuple[User, dict]:
        token = request.headers.get("Authorization")

        if not token:
            raise HTTPException(401)

        payload = self.validate_token(db_session, token, desired_type=TokenType.ACCESS)

        user = User.get_user_by_id(db_session, payload["sub"])
        if not user:
            raise HTTPException(401)

        if self.require_admin is True and user.is_admin is False:
            raise HTTPException(401)

        return user, payload

    @staticmethod
    def validate_token(db_session: DbSession, token: str, desired_type: TokenType) -> dict[str, Any]:
        try:
            payload = jwt.decode(token.split(" ")[-1], JWT_SECRET, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise HTTPException(401)
        except jwt.exceptions.DecodeError:
            raise HTTPException(401)

        ts = int(datetime.datetime.now().timestamp())
        if ts < payload["nbf"] or ts >= payload["exp"]:
            raise HTTPException(401)

        if payload["type"] != desired_type:
            raise HTTPException(401)

        if desired_type == TokenType.REFRESH:
            if BlockedJti.get_blocked_jti_by_jti(db_session, payload["jti"]):
                raise HTTPException(401)
        else:
            if BlockedJti.get_blocked_jti_by_jti(db_session, payload["refresh_token_id"]):
                raise HTTPException(401)

        return payload


UserSession = Annotated[tuple[User, dict], Depends(SessionValidator())]
AdminSession = Annotated[tuple[User, dict], Depends(SessionValidator(require_admin=True))]
