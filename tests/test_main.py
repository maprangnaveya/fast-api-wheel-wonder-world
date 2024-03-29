from fastapi import status


def test_root_returns_correct_data(test_client):
    response = test_client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World! I'm Wheel Wonder World API"}
