from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from core.global_settings import settings
from crud.shortcuts import get_bson_object_id
from crud.user import get_user_by_id
from db.mongodb import AsyncIOMotorClient
from models.broker import BrokerInDB, BrokerIn, BrokerForUpdate


async def get_broker(connection: AsyncIOMotorClient, broker_id: str, raise_exception: bool = False) -> BrokerInDB:  # type: ignore
    row = await connection[settings.mongo_db][
        settings.brokers_collection_name
    ].find_one({"_id": get_bson_object_id(broker_id)})
    print(f">>> get_broker row: {row}")
    if row:
        return BrokerInDB(**row)
    elif raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker does not found",
        )


async def get_brokers_for_user(connection: AsyncIOMotorClient, user_id: str, skip: int = 0, limit: int = 0) -> list[BrokerInDB]:  # type: ignore
    rows = (
        await connection[settings.mongo_db][settings.brokers_collection_name]
        .find({"user_id": ObjectId(user_id)})
        .skip(skip)
        .limit(limit)
        .to_list(length=None)
    )
    return [BrokerInDB(**broker) for broker in rows]


async def create_broker(connection: AsyncIOMotorClient, broker_in: BrokerIn):  # type: ignore
    user = await get_user_by_id(connection, broker_in.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker's user does not found",
        )

    broker = BrokerInDB(**broker_in.model_dump())
    broker.user_id = ObjectId(user.id)
    broker.emails = list(broker.emails)
    broker.mobile_phones = list(broker.mobile_phones)
    broker.branches = list(broker.branches)

    collection = connection[settings.mongo_db][settings.brokers_collection_name]

    new_broker = await collection.insert_one(
        broker.model_dump(by_alias=True, exclude=["id"])
    )

    created_broker = await collection.find_one({"_id": new_broker.inserted_id})
    return BrokerInDB(**created_broker)


async def update_broker_with_db_broker(connection: AsyncIOMotorClient, broker: BrokerForUpdate, db_broker: BrokerInDB):  # type: ignore
    db_broker.emails = list(broker.emails or db_broker.emails)
    db_broker.mobile_phones = list(broker.mobile_phones or db_broker.mobile_phones)
    db_broker.branches = list(broker.branches or db_broker.branches)
    db_broker.updated_at = datetime.utcnow()
    db_broker.user_id = ObjectId(db_broker.id)

    await connection[settings.mongo_db][settings.brokers_collection_name].update_one(
        {"_id": ObjectId(db_broker.id)},
        {"$set": db_broker.model_dump(by_alias=True, exclude=["id", "user_id"])},
    )
    print(f">> updated db_broker: {db_broker}")
    return db_broker


async def update_broker(connection: AsyncIOMotorClient, broker: BrokerForUpdate):  # type: ignore
    db_broker = await get_broker(connection, broker.id)

    return update_broker_with_db_broker(connection, broker, db_broker)


async def delete_broker(connection: AsyncIOMotorClient, id: str) -> int:  # type: ignore
    delete_result = await connection[settings.mongo_db][
        settings.brokers_collection_name
    ].delete_one({"_id": ObjectId(id)})

    return delete_result.deleted_count
