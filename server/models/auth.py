from __future__ import annotations

from typing import Optional

import pydantic
from sqlmodel import Field, Session, SQLModel, select


class BlockedJti(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True)

    @staticmethod
    def get_blocked_jti_by_jti(session: Session, jti: str) -> Optional[BlockedJti]:
        return session.exec(select(BlockedJti).where(BlockedJti.jti == jti)).one_or_none()


class LoginRequest(pydantic.BaseModel):
    username: str
    password: str
    otp: Optional[str] = pydantic.Field(default=None, pattern=r"\d{6}")


class LoginResponse(pydantic.BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(pydantic.BaseModel):
    refresh_token: str


class RefreshTokenResponse(pydantic.BaseModel):
    refresh_token: str
