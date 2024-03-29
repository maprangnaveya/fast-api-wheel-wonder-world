from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from core.global_settings import settings
from crud.broker import get_broker
from crud.shortcuts import get_bson_object_id
from db.mongodb import AsyncIOMotorClient
from models.car import CarInDB, CarIn


def get_collection_cars(connection: AsyncIOMotorClient):  # type: ignore
    return connection[settings.mongo_db][settings.cars_collection_name]


async def get_car(connection: AsyncIOMotorClient, car_id: str, raise_exception: bool = False) -> CarInDB:  # type: ignore
    row = await get_collection_cars(connection).find_one(
        {"_id": get_bson_object_id(car_id)}
    )
    if row:
        return CarInDB(**row)
    elif raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car does not found",
        )


async def get_cars(connection: AsyncIOMotorClient, query: dict | None = None, skip: int = 0, limit: int = 0) -> list[CarInDB]:  # type: ignore
    if query is None:
        query = {}

    rows = (
        await get_collection_cars(connection)
        .find(query)
        .skip(skip)
        .limit(limit)
        .to_list(length=None)
    )

    return [CarInDB(**car) for car in rows]


async def get_cars_for_broker(connection: AsyncIOMotorClient, broker_id: str) -> list[CarInDB]:  # type: ignore
    rows = (
        await get_collection_cars(connection)
        .find({"broker_id": get_bson_object_id(broker_id)})
        .to_list(length=None)
    )
    return [CarInDB(**car) for car in rows]


async def create_car_for_broker(connection: AsyncIOMotorClient, car_in: CarIn):  # type: ignore
    broker = await get_broker(connection, car_in.broker_id)

    if not broker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker does not found",
        )

    car = CarInDB(**car_in.model_dump())
    car.broker_id = ObjectId(broker.id)

    collection = get_collection_cars(connection)

    new_car = await collection.insert_one(car.model_dump(by_alias=True, exclude=["id"]))

    created_car = await collection.find_one({"_id": new_car.inserted_id})
    return CarInDB(**created_car)


async def update_car_with_db_car(connection: AsyncIOMotorClient, car: CarIn, db_car: CarInDB):  # type: ignore
    db_car.brand = car.brand or db_car.brand
    db_car.model = car.model or db_car.model
    db_car.year = car.year or db_car.year
    db_car.color = car.color or db_car.color
    db_car.mileage = car.mileage or db_car.mileage
    db_car.status = car.status or db_car.status
    db_car.offer_price = car.offer_price or db_car.offer_price

    db_car.updated_at = datetime.utcnow()

    collection = get_collection_cars(connection)

    await connection[settings.mongo_db][settings.cars_collection_name].update_one(
        {"_id": ObjectId(db_car.id)},
        {"$set": db_car.model_dump(by_alias=True, exclude=["id", "broker_id"])},
    )
    updated_car = await collection.find_one({"_id": ObjectId(db_car.id)})
    return CarInDB(**updated_car)


async def delete_car(connection: AsyncIOMotorClient, id: str) -> int:  # type: ignore
    delete_result = await get_collection_cars(connection).delete_one(
        {"_id": get_bson_object_id(id)}
    )

    return delete_result.deleted_count
