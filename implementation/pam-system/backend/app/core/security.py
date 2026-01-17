from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _encode_token(payload: Dict[str, Any], secret: str, expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, extra: Dict[str, Any] | None = None) -> str:
    payload = {"sub": subject, "type": "access"}
    if extra:
        payload.update(extra)
    return _encode_token(payload, settings.JWT_SECRET, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES))


def create_refresh_token(subject: str) -> str:
    payload = {"sub": subject, "type": "refresh"}
    return _encode_token(payload, settings.JWT_REFRESH_SECRET, timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS))


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def decode_refresh_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=[settings.JWT_ALGORITHM])


def create_gateway_token(payload: Dict[str, Any]) -> str:
    return _encode_token(
        payload,
        settings.GATEWAY_JWT_SECRET,
        timedelta(minutes=settings.GATEWAY_TOKEN_EXPIRES_MINUTES),
    )
