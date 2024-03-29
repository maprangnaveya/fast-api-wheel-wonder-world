from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.api_v1.api import router as api_router
from core.global_settings import settings
from db.mongodb_utils import connect_to_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up
    connect_to_mongodb(settings.mongodb_url)

    yield

    # shutdown
    # await disconnect_mongodb()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
def root():
    return {"message": f"Hello World! I'm {settings.app_name}"}


app.include_router(api_router, prefix="/api/v1")
