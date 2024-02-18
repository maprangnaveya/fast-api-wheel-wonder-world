from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from core.oauth import get_current_user_for_db
from crud.broker import (
    create_broker,
    get_broker,
    get_brokers_for_user,
    update_broker_with_db_broker,
)
from crud.car import (
    create_car_for_broker,
    delete_car,
    get_car,
    get_cars,
    update_car_with_db_car,
)
from crud.shortcuts import get_bson_object_id
from db.mongodb import get_database, AsyncIOMotorClient
from models.car import CarForDB, CarIn, CarInUpdate, CarOut, Status
from models.user import UserForDB

router = APIRouter()

tags = ["car"]


async def check_is_owner_car(db, *, current_user: UserForDB, current_car: CarForDB):
    brokers_of_user = await get_brokers_for_user(db, current_user.id)
    brokers_id_of_user = [broker.id for broker in brokers_of_user]
    if current_car.broker_id not in brokers_id_of_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only car's broker can do this action",
        )


@router.get(
    "/cars",
    response_model=list[CarOut],
    tags=tags,
    description="Get All Cars by Status, Broker Id",
)
async def get_all_cars_by_status_broker_id(
    status: Status = None,
    broker_id: str = None,
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    query = {}
    if status:
        query["status"] = status.value

    if broker_id:
        query["broker_id"] = get_bson_object_id(broker_id)

    cars = await get_cars(db, query=query)
    return [CarOut(**car.model_dump()) for car in cars]


@router.get("/cars/{car_id}", response_model=CarOut, tags=tags)
async def get_car_by_id(
    car_id: str,
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    car = await get_car(db, car_id, raise_exception=True)
    return CarOut(**car.model_dump())


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


@router.post("/cars/{car_id}", response_model=CarOut, tags=tags)
async def update_car_by_id(
    car_id: str,
    car_update: CarInUpdate = Body(embed=True),
    current_user: UserForDB = Depends(get_current_user_for_db),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    # TODO: Is staff or broker user
    current_car = await get_car(db, car_id, raise_exception=True)
    await check_is_owner_car(db, current_user=current_user, current_car=current_car)

    updated_car = await update_car_with_db_car(db, car_update, current_car)
    return CarOut(**updated_car.model_dump())


@router.delete("/cars/{car_id}", tags=tags, status_code=204)
async def delete_car_by_id(
    car_id: str,
    current_user: UserForDB = Depends(get_current_user_for_db),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    current_car = await get_car(db, car_id, raise_exception=True)
    # TODO: Is staff or broker user
    await check_is_owner_car(db, current_user=current_user, current_car=current_car)

    deleted_count = await delete_car(db, car_id)
    if deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Car not found",
    )
