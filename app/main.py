from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.api_v1.api import router as api_router
from .core.global_settings import settings
from .db.mongodb_utils import connect_to_mongodb, disconnect_mongodb


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


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


app.include_router(api_router, prefix="/api/v1")
