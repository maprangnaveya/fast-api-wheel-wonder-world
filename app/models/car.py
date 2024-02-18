from enum import Enum
from pydantic import Field

from .db_model import DBModelMixin, PyObjectId
from .read_write_model import RWModel


class Status(str, Enum):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"


class BaseCar(RWModel):
    brand: str = Field(...)
    model: str = Field(...)
    year: int | None = Field(default_factory=None)
    color: str = Field(...)
    mileage: float = Field(default_factory=0.0)
    offer_price: float = Field(default=0.0)
    status: Status = Field(default=Status.INACTIVE)


class BaseCarWithBroker(BaseCar):
    broker_id: PyObjectId = Field(...)


class CarInDB(DBModelMixin, BaseCarWithBroker):
    pass


class CarOut(CarInDB):
    pass


class CarIn(BaseCarWithBroker):
    pass


class CarInUpdate(BaseCar):
    pass
