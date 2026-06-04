from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
import hashlib

from .config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _normalize_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return digest


def hash_password(password: str) -> str:
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(password: str, hashed: str) -> bool:
    normalized = _normalize_password(password)
    return pwd_context.verify(normalized, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)