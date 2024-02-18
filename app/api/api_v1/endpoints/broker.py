from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status

from core.oauth import get_current_user_for_db
from crud.broker import (
    create_broker,
    get_broker,
    get_brokers_for_user,
    update_broker_with_db_broker,
)
from db.mongodb import get_database, AsyncIOMotorClient
from models.broker import BrokerForUpdate, BrokerIn, BrokerOut
from models.user import UserForDB

router = APIRouter()

tags = ["broker"]


@router.get("/brokers/me", response_model=list[BrokerOut], tags=tags)
async def get_brokers_for_request_user(
    current_user: Annotated[UserForDB, Depends(get_current_user_for_db)],
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    brokers = await get_brokers_for_user(db, current_user.id)
    return [BrokerOut(**broker.model_dump()) for broker in brokers]


@router.get("/brokers/{broker_id}", response_model=BrokerOut, tags=tags)
async def get_broker_by_id(
    broker_id: str,
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    broker = await get_broker(db, broker_id)
    return BrokerOut(**broker.model_dump())


@router.post("/brokers", response_model=BrokerOut, tags=tags)
async def create_new_broker(
    broker: BrokerIn = Body(embed=True),
    current_user: UserForDB = Depends(get_current_user_for_db),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    if not broker.user_id:
        broker.user_id = ObjectId(current_user.id)

    async with await db.start_session() as s:
        async with s.start_transaction():
            db_broker = await create_broker(db, broker)

            return BrokerOut(**db_broker.model_dump())


@router.patch("/brokers/{broker_id}", response_model=BrokerOut, tags=tags)
async def update_broker_by_id(
    broker_id: str,
    updated_broker: BrokerForUpdate = Body(embed=True),
    current_user: UserForDB = Depends(get_current_user_for_db),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    current_broker = await get_broker(db, broker_id, raise_exception=True)
    if current_broker.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner broker can do this action",
        )

    updated_broker = await update_broker_with_db_broker(
        db, updated_broker, current_broker
    )
    return BrokerOut(**updated_broker.model_dump())
