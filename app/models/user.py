from pydantic import Field, EmailStr

from core.security import generate_salt, get_password_hash, verify_password

from .db_model import DBModelMixin
from .read_write_model import RWModel


class BaseUser(RWModel):
    email: EmailStr = Field(...)
    name: str = Field(alias="full_name")


class UserForDB(DBModelMixin, BaseUser):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str):
        return verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str):
        self.salt = generate_salt()
        self.hashed_password = get_password_hash(self.salt + password)


class User(BaseUser):
    token: str


class UserForLogin(RWModel):
    email: EmailStr
    password: str


class UserForResponse(RWModel):
    user: User
