from bson import ObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr


from crud.user import get_user
from db.mongodb import AsyncIOMotorClient


async def check_is_email_does_exists(
    conn: AsyncIOMotorClient, email: EmailStr  # type: ignore
):

    user_by_email = await get_user(conn, email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


def get_bson_object_id(object_id) -> ObjectId:
    try:
        return ObjectId(object_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object id is invalid",
        )


def get_total_skip_from_page_number(*, page, page_size):
    return (page - 1) * page_size
