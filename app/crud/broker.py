from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr
from core.global_settings import settings
from crud.user import get_user_by_id
from db.mongodb import AsyncIOMotorClient
from models.broker import BrokerForDB, BrokerIn, BrokerForUpdate


async def get_broker(connection: AsyncIOMotorClient, broker_id: str) -> BrokerForDB:  # type: ignore
    try:
        row = await connection[settings.mongo_db][
            settings.brokers_collection_name
        ].find_one({"_id": ObjectId(broker_id)})
        print(f">>> get_broker row: {row}")
        if row:
            return BrokerForDB(**row)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker does not found",
        )


async def get_brokers_for_user(connection: AsyncIOMotorClient, user_id: str) -> list[BrokerForDB]:  # type: ignore

    rows = (
        await connection[settings.mongo_db][settings.brokers_collection_name]
        .find({"user_id": ObjectId(user_id)})
        .to_list(length=None)
    )
    return [BrokerForDB(**broker) for broker in rows]


async def create_broker(connection: AsyncIOMotorClient, broker: BrokerIn):  # type: ignore

    user = await get_user_by_id(connection, broker.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker's user does not found",
        )

    broker.emails = list(broker.emails)
    broker.mobile_phones = list(broker.mobile_phones)
    broker.branches = list(broker.branches)

    collection = connection[settings.mongo_db][settings.brokers_collection_name]

    new_broker = await collection.insert_one(
        broker.model_dump(by_alias=True, exclude=["id"])
    )

    created_broker = await collection.find_one({"_id": new_broker.inserted_id})
    return BrokerForDB(**created_broker)


async def update_broker(connection: AsyncIOMotorClient, broker: BrokerForUpdate):  # type: ignore
    db_broker = await get_broker(connection, broker.id)

    db_broker.emails = broker.emails or db_broker.emails
    db_broker.mobile_phones = broker.mobile_phones or db_broker.mobile_phones
    db_broker.branches = broker.branches or db_broker.branches
    db_broker.updated_at = datetime.utcnow()

    await connection[settings.mongo_db][settings.brokers_collection_name].update_one(
        {"id": db_broker.id}, {"$set": db_broker.model_dump()}
    )
    print(f">> updated db_broker: {db_broker}")
    return db_broker


async def delete_broker(connection: AsyncIOMotorClient, id: str) -> int:  # type: ignore
    delete_result = await connection[settings.mongo_db][
        settings.brokers_collection_name
    ].delete_one({"_id": ObjectId(id)})

    return delete_result.deleted_count
