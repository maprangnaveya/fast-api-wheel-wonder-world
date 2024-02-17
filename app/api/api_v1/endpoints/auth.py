from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status

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

    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # token = create_access_token(
    #     data={"username": dbuser.username}, expires_delta=access_token_expires
    # )
    return UserForResponse(user=User(**dbuser.model_dump(), token="faketoken"))


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
            # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            # token = create_access_token(
            #     data={"username": dbuser.username}, expires_delta=access_token_expires
            # )

            return UserForResponse(user=User(**dbuser.model_dump(), token="faketoken"))
