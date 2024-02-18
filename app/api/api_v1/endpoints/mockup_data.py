from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import EmailStr

from core.oauth import get_current_active_user, is_staff_user
from crud.broker import get_broker, get_collection_broker
from crud.car import get_collection_cars
from crud.user import update_user, update_user_is_staff
from db.mongodb import get_database, AsyncIOMotorClient
from models.mockup_data import cars_mockup_data

router = APIRouter()

tags = ["load_mockup_data"]


@router.patch("/test/cars/{broker_id}", tags=tags)
async def load_mockup_cars_data(
    broker_id: str,
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    current_broker = await get_broker(db, broker_id, raise_exception=True)
    date_now = datetime.utcnow()

    cars = [
        {
            **car,
            "broker_id": ObjectId(current_broker.id),
            "created_at": date_now,
            "updated_at": date_now,
        }
        for car in cars_mockup_data
    ]
    get_collection_cars(db).insert_many(cars)
    return {"message": "Broker mockup data created successfully"}
