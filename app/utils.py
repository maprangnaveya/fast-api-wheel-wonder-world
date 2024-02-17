from motor.motor_asyncio import AsyncIOMotorClient


async def init_mongo(db_name: str, db_url: str):
    """
    Args:
        db_name:
        db_url:

    Returns:
        (mongo_client, mongo_database)

    """
    mongo_client = AsyncIOMotorClient(db_url)
    mongo_database = mongo_client[db_name]

    return (mongo_client, mongo_database)
