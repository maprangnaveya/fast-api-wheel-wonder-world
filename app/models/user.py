from pydantic import Field, EmailStr

from .read_write_model import RWModel


class BaseUser(RWModel):
    email: EmailStr = Field(...)
    name: str = Field(alias="full_name")
