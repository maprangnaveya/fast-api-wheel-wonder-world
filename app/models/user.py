from pydantic import Field, EmailStr

from .db_model import DBModelMixin
from .read_write_model import RWModel


class BaseUser(RWModel):
    email: EmailStr = Field(...)
    name: str = Field(alias="full_name")


class UserForDB(DBModelMixin, BaseUser):
    salt: str = ""
    hashed_password: str = ""
class User(BaseUser):
    token: str


class UserForLogin(RWModel):
    email: EmailStr
    password: str


class UserForResponse(RWModel):
    user: User
