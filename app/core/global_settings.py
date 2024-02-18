import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Represents the configuration settings for the application.

    Args:
        environment (str): The environment in which the application is running. Defaults to "local".
        app_name (str): The application name. Defaults to "Wheel Wonder World API".

    """

    environment: str = os.getenv("ENVIRONMENT", "local")
    app_name: str = os.getenv("APP_NAME", "Wheel Wonder World API")

    # MongoDB
    mongo_port: int = int(os.getenv("MONGO_PORT", 27017))
    mongo_user: str = os.getenv("MONGO_USERNAME", "mongo_user")
    mongo_pass: str = os.getenv("MONGO_PASSWORD", "mongo_pass")
    mongo_db: str = os.getenv("MONGO_DATABASE", "wheel_db")

    mongodb_url: str = f"mongodb://{mongo_user}:{mongo_pass}@mongodb:{mongo_port}"

    # MongoDB collections
    users_collection_name: str = "users"
    brokers_collection_name: str = "brokers"

    jwt_secret_key: str = os.getenv(
        "SECRET_KEY", "03850f6de136cbfbac0ffb32e35cfde826d262c5d117331de42e418ddf7b02ea"
    )


settings = Settings()


@lru_cache
def get_settings():
    return settings
