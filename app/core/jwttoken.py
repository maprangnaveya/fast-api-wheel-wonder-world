from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt

from models.jwttoken import TokenData

# from app.main import TokenData
from .global_settings import settings

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(*, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if not expires_delta:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f">>> payload: {payload}")
        print(f">>> username: {username}")
        if username is None:
            raise credentials_exception

        token_data = TokenData(user_email=username)
        print(f">>> token_data: {token_data}")
        return token_data
    except JWTError:
        raise credentials_exception
