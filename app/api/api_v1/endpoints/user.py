from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from core.oauth import get_current_active_user
from crud.user import update_user
from db.mongodb import get_database, AsyncIOMotorClient
from models.user import (
    User,
    UserForUpdate,
)

router = APIRouter()

tags = ["profile"]


@router.patch("/profile/me", tags=tags)
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
    return updated_user
