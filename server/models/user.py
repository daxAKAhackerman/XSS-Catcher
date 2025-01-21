from __future__ import annotations

import random
import re
import string
from typing import Optional, Self, cast

import pydantic
from sqlmodel import Field, Session, SQLModel, select
from werkzeug.security import check_password_hash, generate_password_hash


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    first_login: bool
    is_admin: bool
    mfa_secret: Optional[str] = Field(default=None)

    # clients: list["Client"] = Relationship(back_populates="owner")
    # api_keys: list["ApiKey"] = Relationship(back_populates="owner")

    def get_id(self) -> int:
        return cast(int, self.id)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_password() -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for i in range(12))

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> Optional[User]:
        return session.exec(select(User).where(User.username == username)).one_or_none()

    @staticmethod
    def get_user_by_id(session: Session, id: int) -> Optional[User]:
        return session.get(User, id)


class CreateUserRequest(pydantic.BaseModel):
    username: str


class CreateUserResponse(pydantic.BaseModel):
    password: str


class ChangePasswordRequest(pydantic.BaseModel):
    password1: str
    password2: str
    old_password: str

    @pydantic.field_validator("password1", mode="after")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"\d", v):
            raise ValueError("password must contain a number")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain a lower case letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain an upper case letter")
        return v

    @pydantic.model_validator(mode="after")
    def password_match(self) -> Self:
        if self.password1 != self.password2:
            raise ValueError("passwords don't match")
        return self


class ResetPasswordResponse(pydantic.BaseModel):
    password: str


class GetCurrentUserResponse(pydantic.BaseModel):
    id: int
    username: str
    first_login: bool
    is_admin: bool
    mfa: bool
