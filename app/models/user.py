from pydantic import Field, EmailStr

from .read_write_model import RWModel


class BaseUser(RWModel):
    email: EmailStr = Field(...)
    name: str = Field(alias="full_name")

class User(BaseUser):
    token: str


class UserForLogin(RWModel):
    email: EmailStr
    password: str


class UserForResponse(RWModel):
    user: User
