import os

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
