from typing import Optional

import pydantic


class Login(pydantic.BaseModel):
    username: str
    password: str
    otp: Optional[str] = pydantic.Field(default=None)


class LoginResponse(pydantic.BaseModel):
    access_token: str
    refresh_token: str


class RefreshToken(pydantic.BaseModel):
    refresh_token: str


class RefreshTokenResponse(RefreshToken):
    pass
