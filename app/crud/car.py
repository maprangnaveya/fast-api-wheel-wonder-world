from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from core.global_settings import settings
from crud.broker import get_broker
from crud.shortcuts import get_bson_object_id
from crud.user import get_user_by_id
from db.mongodb import AsyncIOMotorClient
from models.broker import BrokerIn, BrokerForUpdate
from models.car import CarForDB, CarIn


def get_collection_cars(connection: AsyncIOMotorClient):  # type: ignore
    return connection[settings.mongo_db][settings.cars_collection_name]



async def get_cars_for_broker(connection: AsyncIOMotorClient, broker_id: str) -> list[CarForDB]:  # type: ignore
    rows = (
        await get_collection_cars(connection)
        .find({"broker_id": get_bson_object_id(broker_id)})
        .to_list(length=None)
    )
    return [CarForDB(**car) for car in rows]


async def create_car_for_broker(connection: AsyncIOMotorClient, car_in: CarIn):  # type: ignore
    broker = await get_broker(connection, car_in.broker_id)

    if not broker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker does not found",
        )

    car = CarForDB(**car_in.model_dump())
    car.broker_id = ObjectId(broker.id)

    collection = get_collection_cars(connection)

    new_car = await collection.insert_one(car.model_dump(by_alias=True, exclude=["id"]))

    created_car = await collection.find_one({"_id": new_car.inserted_id})
    return CarForDB(**created_car)

    )
    return db_car

