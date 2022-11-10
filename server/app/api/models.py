from typing import Literal, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, validator


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
