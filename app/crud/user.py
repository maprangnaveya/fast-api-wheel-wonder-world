from datetime import datetime
from bson import ObjectId
from pydantic import EmailStr

from core.global_settings import settings
from db.mongodb import AsyncIOMotorClient
from models.user import UserForDB, UserForCreate, UserForUpdate


async def get_user_by_id(connection: AsyncIOMotorClient, id: str) -> UserForDB:  # type: ignore
    row = await connection[settings.mongo_db][settings.users_collection_name].find_one(
        {"_id": ObjectId(id)}
    )
    print(f">>> get_user row: {row}")
    if row:
        return UserForDB(**row)


async def get_user(connection: AsyncIOMotorClient, email: EmailStr) -> UserForDB:  # type: ignore
    row = await connection[settings.mongo_db][settings.users_collection_name].find_one(
        {"email": email}
    )
    print(f">>> get_user row: {row}")
    if row:
        return UserForDB(**row)


async def create_user(connection: AsyncIOMotorClient, user: UserForCreate) -> UserForDB:  # type: ignore
    """
    A unique `id` will be created and provided in the response.
    """
    db_user = UserForDB(
        **user.model_dump(),
    )
    # hash password
    db_user.change_password(user.password)

    collection = connection[settings.mongo_db][settings.users_collection_name]

    new_user = await collection.insert_one(
        db_user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await collection.find_one({"_id": new_user.inserted_id})

    return UserForDB(**created_user)


async def update_user(connection: AsyncIOMotorClient, email: EmailStr, user: UserForUpdate) -> UserForDB:  # type: ignore
    db_user = await get_user(connection, email)

    db_user.email = user.email or db_user.email
    db_user.name = user.name or db_user.name
    if user.password:
        db_user.change_password(user.password)

    updated_at = await connection[settings.mongo_db][
        settings.users_collection_name
    ].update_one({"email": db_user.email}, {"$set": db_user.model_dump()})
    db_user.updated_at = updated_at
    return db_user
