from pydantic import BaseModel, Field


class LoginModel(BaseModel):
    username: str
    password: str


class ClientPostModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., max_length=128)
