import logging

from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db


def connect_to_mongodb(db_url: str):
    logging.info("....connecting to MongoDB....")

    db.client = AsyncIOMotorClient(db_url)

    logging.info("....MongoDB connected....")


async def disconnect_mongodb():
    logging.info("....disconnecting MongoDB....")

    # if db.client:
    #     db.client.close()

    logging.info("....MongoDB disconnected....")
