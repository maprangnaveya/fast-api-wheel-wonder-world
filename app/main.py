from contextlib import asynccontextmanager
from fastapi import FastAPI

from .config import Settings
from .utils import init_mongo

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up
    app.state.mongo_client, app.state.mongo_db = await init_mongo(
        settings.mongo_db,
        settings.mongodb_url,
    )
    yield
    # shutdown


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
