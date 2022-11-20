import re
from typing import List, Literal, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, validator

DATA_TO_GATHER = {"local_storage", "session_storage", "cookies", "origin_url", "referrer", "dom", "screenshot", "fingerprint"}


class LoginModel(BaseModel):
    username: str
    password: str


class ClientPostModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., max_length=128)


class ClientPatchModel(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=32)
    description: Optional[str] = Field(max_length=128)
    owner: Optional[int]
    mail_to: Union[EmailStr, None, Literal[""]]
    webhook_url: Union[AnyHttpUrl, None, Literal[""]]


class SettingsPatchModel(BaseModel):
    smtp_host: Optional[str] = Field(max_length=256)
    smtp_port: Optional[int] = Field(gt=0, lt=65536)
    starttls: Optional[bool]
    ssl_tls: Optional[bool]
    mail_from: Optional[EmailStr]
    mail_to: Union[EmailStr, None, Literal[""]]
    smtp_user: Optional[str] = Field(max_length=128)
    smtp_pass: Optional[str] = Field(max_length=128)
    webhook_url: Union[AnyHttpUrl, None, Literal[""]]


class SmtpTestPostModel(BaseModel):
    mail_to: EmailStr


class WebhookTestPostModel(BaseModel):
    webhook_url: AnyHttpUrl


class RegisterModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)


class ChangePasswordModel(BaseModel):
    password1: str = Field(..., min_length=8)
    password2: str
    old_password: str

    @validator("password1")
    def password_complexity(cls, v, values, **kwargs):
        if not re.search(r"\d", v):
            raise ValueError("password must contain a number")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain a lower case letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain an upper case letter")
        return v

    @validator("password2")
    def password_match(cls, v, values, **kwargs):
        if "password1" in values and v != values["password1"]:
            raise ValueError("passwords don't match")
        return v


class UserPatchModel(BaseModel):
    is_admin: bool


class XssGenerateModel(BaseModel):
    client_id: int
    url: AnyHttpUrl
    xss_type: Literal["r", "s"]
    code_type: Literal["html", "js"]
    to_gather: List[str]
    tags: List[str]

    @validator("to_gather")
    def to_gather_validator(cls, v, values, **kwargs):
        for value in v:
            if value not in DATA_TO_GATHER:
                raise ValueError(f"values in to_gather must be in {DATA_TO_GATHER}")
        return v
