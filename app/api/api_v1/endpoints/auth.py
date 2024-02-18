from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

from core.jwttoken import create_access_token
from crud.shortcuts import check_is_email_does_exists
from crud.user import create_user, get_user
from db.mongodb import get_database, AsyncIOMotorClient
from models.user import User, UserForCreate, UserForLogin, UserForResponse

router = APIRouter()

tags = ["authentication"]


@router.post("/auth/login", response_model=UserForResponse, tags=tags)
async def login(
    user: Annotated[UserForLogin, Body(embed=True)],
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    dbuser = await get_user(db, user.email)
    if not dbuser or not dbuser.check_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email or password incorrect",
        )

    token = create_access_token(
        data={"email": dbuser.email}, expires_delta=timedelta(days=1)
    )
    return UserForResponse(user=User(**dbuser.model_dump(), token=token))


@router.post(
    "/auth/register",
    response_model=UserForResponse,
    tags=tags,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserForCreate = Body(..., embed=True),
    db: AsyncIOMotorClient = Depends(get_database),  # type: ignore
):
    await check_is_email_does_exists(db, user.email)

    async with await db.start_session() as s:
        async with s.start_transaction():
            dbuser = await create_user(db, user)
            token = create_access_token(
                data={"email": dbuser.email}, expires_delta=timedelta(days=1)
            )

            return UserForResponse(user=User(**dbuser.model_dump(), token=token))
