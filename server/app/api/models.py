import re
from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from werkzeug.exceptions import BadRequest

UNDEFINED = "__UNDEFINED__"
UNDEFINED_TYPE = Literal["__UNDEFINED__"]


class DataToGather(StrEnum):
    LOCAL_STORAGE = "local_storage"
    SESSION_STORAGE = "session_storage"
    COOKIES = "cookies"
    ORIGIN_URL = "origin_url"
    REFERRER = "referrer"
    DOM = "dom"
    SCREENSHOT = "screenshot"
    FINGERPRINT = "fingerprint"


class XssType(StrEnum):
    REFLECTED = "reflected"
    STORED = "stored"


class ShortXssType(StrEnum):
    REFLECTED = "r"
    STORED = "s"


class CodeType(StrEnum):
    HTML = "html"
    JAVASCRIPT = "js"


class LoginModel(BaseModel):
    username: str
    password: str
    otp: Optional[str] = Field(default=None, pattern=r"\d{6}")


class CreateClientModel(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    description: Optional[str] = None


class EditClientModel(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=32)
    owner: Optional[int] = None
    description: Optional[str] = UNDEFINED
    mail_to: Optional[str] = UNDEFINED
    webhook_url: Optional[str] = UNDEFINED


class EditSettingsModel(BaseModel):
    smtp_host: Optional[str] = UNDEFINED
    smtp_port: Optional[int | UNDEFINED_TYPE] = Field(default=UNDEFINED, ge=1, le=65535)
    starttls: Optional[bool | UNDEFINED_TYPE] = UNDEFINED
    ssl_tls: Optional[bool | UNDEFINED_TYPE] = UNDEFINED
    mail_from: Optional[str] = UNDEFINED
    mail_to: Optional[str] = UNDEFINED
    smtp_user: Optional[str] = UNDEFINED
    smtp_pass: Optional[str] = UNDEFINED
    webhook_url: Optional[str] = UNDEFINED
    webhook_type: Optional[Literal[0, 1, 2] | UNDEFINED_TYPE] = UNDEFINED


class TestSmtpSettingsModel(BaseModel):
    mail_to: str


class TestWebhookSettingsModel(BaseModel):
    webhook_url: str


class RegisterModel(BaseModel):
    username: str = Field(min_length=1)


class ChangePasswordModel(BaseModel):
    password1: str = Field(min_length=8)
    password2: str
    old_password: str

    @field_validator("password1", mode="after")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"\d", v):
            raise BadRequest("password must contain a number")
        if not re.search(r"[a-z]", v):
            raise BadRequest("password must contain a lower case letter")
        if not re.search(r"[A-Z]", v):
            raise BadRequest("password must contain an upper case letter")
        return v

    @model_validator(mode="after")
    def password_match(self):
        if self.password1 != self.password2:
            raise BadRequest("passwords don't match")
        return self


class EditUserModel(BaseModel):
    is_admin: bool | UNDEFINED_TYPE = UNDEFINED


class GenerateXssPayloadModel(BaseModel):
    client_id: int
    url: str
    xss_type: ShortXssType
    code_type: CodeType
    to_gather: list[DataToGather]
    tags: list[str]
    custom_js: str


class GetAllXssModel(BaseModel):
    client_id: int
    type: XssType


class GetAllXssLootModel(BaseModel):
    client_id: int


class SetMfaModel(BaseModel):
    secret: str = Field(pattern=r"[A-Z2-7]{32}")
    otp: str = Field(pattern=r"\d{6}")
