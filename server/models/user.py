from __future__ import annotations

import random
import string

from sqlmodel import Field, Relationship, Session, SQLModel, select
from werkzeug.security import generate_password_hash


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password_hash: str | None = Field(default=None)
    first_login: bool | None = Field(default=True)
    is_admin: bool | None = Field(default=False)
    mfa_secret: str | None = Field(default=None)

    # clients: list["Client"] = Relationship(back_populates="owner")
    # api_keys: list["ApiKey"] = Relationship(back_populates="owner")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def generate_password() -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for i in range(12))

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> User | None:
        return session.exec(select(User).where(User.username == username)).one_or_none()


class UserCreate(SQLModel):
    username: str


class UserCreateResponse(SQLModel):
    password: str


class UserChangePassword(SQLModel):
    old_password: str
    password1: str
    password2: str
