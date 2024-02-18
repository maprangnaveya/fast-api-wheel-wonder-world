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
from crud.car import create_car_for_broker, get_car, get_cars, update_car_with_db_car
from db.mongodb import get_database, AsyncIOMotorClient
from models.broker import BrokerForUpdate, BrokerIn, BrokerOut
from models.car import CarIn, CarInUpdate, CarOut
from models.user import UserForDB

router = APIRouter()

tags = ["car"]


@router.get("/cars", response_model=list[CarOut], tags=tags)
async def get_all_cars(
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    cars = await get_cars(db)
    return [CarOut(**car.model_dump()) for car in cars]
@router.post("/cars", response_model=CarOut, tags=tags)
async def create_new_car(
    car: CarIn = Body(embed=True),
    current_user: UserForDB = Depends(get_current_user_for_db),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):

    async with await db.start_session() as s:
        async with s.start_transaction():
            db_car = await create_car_for_broker(db, car)

            return CarOut(**db_car.model_dump())

