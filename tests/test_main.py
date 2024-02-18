from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_returns_correct_data():
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World! I'm Wheel Wonder World API"}
