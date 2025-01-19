import datetime
import random
import string
import uuid
from enum import StrEnum
from typing import Annotated, Optional

import jwt
from database import DbSession
from fastapi import Depends, HTTPException, Request
from models.auth import BlockedJti
from models.user import User

# TODO: set different value for production
ACCESS_TOKEN_LIFETIME = 60 * 60  # in seconds


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def create_jwt_secret() -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(12))


# TODO: use create_jwt_secret for production
jwt_secret = "test_secret"


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

    return jwt.encode(payload, jwt_secret, algorithm="HS256"), jti


def validate_session(request: Request, db_session: DbSession) -> tuple[User, dict]:
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(401)

    return validate_token(db_session, token, desired_type=TokenType.ACCESS)


def validate_token(db_session: DbSession, token: str, desired_type: TokenType) -> tuple[User, dict]:
    try:
        payload = jwt.decode(token.split(" ")[-1], jwt_secret, algorithms=["HS256"])
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

    user = User.get_user_by_id(db_session, payload["sub"])
    if not user:
        raise HTTPException(401)

    return user, payload


UserSession = Annotated[tuple[User, dict], Depends(validate_session)]
