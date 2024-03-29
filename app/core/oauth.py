from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.jwttoken import verify_token
from crud.user import get_user
from db.mongodb import get_database, AsyncIOMotorClient
from models.user import User, UserInDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user_for_db(
    db: AsyncIOMotorClient = Depends(get_database), token: str = Depends(oauth2_scheme)  # type: ignore
) -> UserInDB:

    print(f">>> get_current_user token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    token_data = verify_token(token, credentials_exception)

    db_user = await get_user(db, token_data.user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return db_user


async def get_current_user(
    db: AsyncIOMotorClient = Depends(get_database), token: str = Depends(oauth2_scheme)  # type: ignore
) -> User:

    db_user = await get_current_user_for_db(db, token)
    user = User(**db_user.model_dump(), token=token)
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def is_staff_user(current_user: User | UserInDB):
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allow to do this action",
        )
