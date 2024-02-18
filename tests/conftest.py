from fastapi.testclient import TestClient
from pytest import fixture

from db.mongodb import get_database


@fixture(scope="session")
def test_client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    import asyncio

    _db = asyncio.run(get_database())
