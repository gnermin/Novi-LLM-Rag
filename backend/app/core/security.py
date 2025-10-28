from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from pydantic import SecretStr
import os, secrets

from app.core.config import settings
from app.core.db import get_db

security = HTTPBearer()


def _get_signing_key() -> str:
    """
    Vrati stvarni string ključ za JWT:
    - podržava pydantic SecretStr
    - čita iz SECRET_KEY / SESSION_SECRET env varijabli
    - ima siguran dev fallback da se nikad ne sruši
    """
    key = settings.SECRET_KEY
    if isinstance(key, SecretStr):
        key = key.get_secret_value()
    # fallback na env ako je iz bilo kog razloga prazno
    key = key or os.getenv("SECRET_KEY") or os.getenv("SESSION_SECRET")
    if not isinstance(key, (str, bytes)) or not key:
        key = secrets.token_urlsafe(64)  # dev fallback
    if isinstance(key, bytes):
        return key.decode("utf-8")
    return key


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _get_signing_key(), algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, _get_signing_key(), algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None or not isinstance(user_id, str):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
