from __future__ import annotations

import random
import string
from typing import Optional, cast

import pydantic
from sqlmodel import Field, Session, SQLModel, select
from werkzeug.security import check_password_hash, generate_password_hash


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
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


class CreateUser(pydantic.BaseModel):
    username: str


class CreateUserResponse(pydantic.BaseModel):
    password: str
