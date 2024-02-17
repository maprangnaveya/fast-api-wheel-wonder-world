from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
    client: AsyncIOMotorClient = None  # type: ignore


db = DataBase()


async def get_database() -> AsyncIOMotorClient:  # type: ignore
    return db.client
