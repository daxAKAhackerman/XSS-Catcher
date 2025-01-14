import datetime
import random
import string
import uuid
from enum import StrEnum
from typing import Annotated

import jwt
from database import DbSession
from fastapi import Depends, HTTPException, Request
from models.user import User

ACCESS_TOKEN_LIFETIME = 300  # in seconds


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def create_jwt_secret() -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(12))


jwt_secret = create_jwt_secret()


def create_token(user_id: int, token_type: TokenType):
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

    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def validate_session(request: Request, db_session: DbSession) -> User:
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(401)

    try:
        payload = jwt.decode(token.split(" ")[-1], jwt_secret, algorithms=["HS256"])
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(401)

    ts = int(datetime.datetime.now().timestamp())
    if ts < payload["nbf"] or ts >= payload["exp"]:
        raise HTTPException(401)

    if payload["type"] != TokenType.ACCESS:
        raise HTTPException(401)

    user = User.get_user_by_id(db_session, payload["sub"])
    if not user:
        raise HTTPException(401)

    return user


UserSession = Annotated[User, Depends(validate_session)]


def get_user_from_refresh_token(db_session: DbSession, refresh_token: str) -> User:
    try:
        payload = jwt.decode(refresh_token, jwt_secret, algorithms=["HS256"])
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(401)

    ts = int(datetime.datetime.now().timestamp())
    if ts < payload["nbf"] or ts >= payload["exp"]:
        raise HTTPException(401)

    if payload["type"] != TokenType.REFRESH:
        raise HTTPException(401)

    # Implement blocklist
    # if session.id in BlocklistStore.get_blocklist_from_cache().entries:
    #     raise HTTPException(401)

    user = User.get_user_by_id(db_session, payload["sub"])
    if not user:
        raise HTTPException(401)

    return user
