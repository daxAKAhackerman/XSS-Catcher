from typing import Optional

from sqlmodel import SQLModel


class Login(SQLModel):
    username: str
    password: str
    otp: Optional[str]
