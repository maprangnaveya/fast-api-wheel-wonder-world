from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from core.oauth import get_current_active_user, get_current_user_for_db
from crud.broker import create_broker, get_broker, get_brokers_for_user
from db.mongodb import get_database, AsyncIOMotorClient
from models.broker import BrokerForUpdate, BrokerIn, BrokerOut
from models.user import User, UserForDB

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
        broker.user_id = current_user.id

    async with await db.start_session() as s:
        async with s.start_transaction():
            db_broker = await create_broker(db, broker)

            return BrokerOut(**db_broker.model_dump())
