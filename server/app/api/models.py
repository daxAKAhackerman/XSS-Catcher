from typing import Literal, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field


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
