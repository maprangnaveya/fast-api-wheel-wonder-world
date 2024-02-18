from pydantic import Field, EmailStr

from .db_model import DBModelMixin, PyObjectId
from .read_write_model import RWModel


class BaseBranch(RWModel):
    name: str = Field(...)
    address: str = Field(default_factory="")
    phones: set[str] = Field(default_factory=set)


class BranchForDB(DBModelMixin, BaseBranch):
    pass

