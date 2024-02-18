from enum import Enum
from pydantic import Field

from .db_model import DBModelMixin, PyObjectId
from .read_write_model import RWModel


class Status(str, Enum):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"


class BaseCar(RWModel):
    broker_id: PyObjectId = Field(...)
    brand: str = Field(...)
    model: str = Field(...)
    year: int | None = Field(default_factory=None)
    color: str = Field(...)
    mileage: float = Field(default_factory=0.0)
    status: Status = Field(default_factory=Status.INACTIVE)


class CarForDB(DBModelMixin, BaseCar):
    pass


class CarOut(CarForDB):
    pass


class CarIn(BaseCar):
    broker_id: PyObjectId | None = Field(default=None)
