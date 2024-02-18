from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr

from core.global_settings import settings
from db.mongodb import AsyncIOMotorClient
from models.user import UserInDB, UserForCreate, UserForUpdate


async def get_user_by_id(connection: AsyncIOMotorClient, id: str) -> UserInDB:  # type: ignore
    row = await connection[settings.mongo_db][settings.users_collection_name].find_one(
        {"_id": ObjectId(id)}
    )
    print(f">>> get_user row: {row}")
    if row:
        return UserInDB(**row)


async def get_user(connection: AsyncIOMotorClient, email: EmailStr, raise_exception: bool = False) -> UserInDB:  # type: ignore
    row = await connection[settings.mongo_db][settings.users_collection_name].find_one(
        {"email": email}
    )
    print(f">>> get_user row: {row}")
    if row:
        return UserInDB(**row)
    elif raise_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not found",
        )


async def create_user(connection: AsyncIOMotorClient, user: UserForCreate) -> UserInDB:  # type: ignore
    """
    A unique `id` will be created and provided in the response.
    """
    db_user = UserInDB(
        **user.model_dump(),
    )
    # hash password
    db_user.change_password(user.password)

    collection = connection[settings.mongo_db][settings.users_collection_name]

    new_user = await collection.insert_one(
        db_user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await collection.find_one({"_id": new_user.inserted_id})

    return UserInDB(**created_user)


async def update_user(connection: AsyncIOMotorClient, email: EmailStr, user: UserForUpdate) -> UserInDB:  # type: ignore
    db_user = await get_user(connection, email)

    db_user.name = user.name or db_user.name
    if user.password:
        db_user.change_password(user.password)

    db_user.updated_at = datetime.utcnow()

    _updated_at = await connection[settings.mongo_db][
        settings.users_collection_name
    ].update_one(
        {"email": db_user.email},
        {"$set": db_user.model_dump(by_alias=True, exclude=["id", "email"])},
    )
    return db_user


async def update_user_is_staff(connection: AsyncIOMotorClient, email: EmailStr, is_staff: bool) -> UserInDB:  # type: ignore
    db_user = await get_user(connection, email, raise_exception=True)

    db_user.is_staff = is_staff
    db_user.updated_at = datetime.utcnow()

    _updated_at = await connection[settings.mongo_db][
        settings.users_collection_name
    ].update_one(
        {"email": db_user.email},
        {"$set": db_user.model_dump(by_alias=True, exclude=["id", "email"])},
    )
    return db_user
