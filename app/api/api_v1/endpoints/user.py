from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import EmailStr

from core.oauth import get_current_active_user, is_staff_user
from crud.user import get_user, update_user, update_user_is_staff
from db.mongodb import get_database, AsyncIOMotorClient
from models.user import (
    User,
    UserForUpdate,
)

router = APIRouter()

tags = ["profile"]


@router.patch("/profile/me", tags=tags, response_model=User)
async def update_my_user_info(
    user: UserForUpdate = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    if user.email and user.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allow to update email",
        )
    updated_user = await update_user(db, current_user.email, user)
    return User(**updated_user.model_dump())


@router.post("/profile/{user_email}/is_staff", tags=tags, response_model=User)
async def update_user_is_staff_status(
    user_email: EmailStr,
    is_staff: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    is_staff_user()
    updated_user = await update_user_is_staff(db, user_email, is_staff)
    return User(**updated_user.model_dump())
