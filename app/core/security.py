from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import bcrypt
from jose import JWTError, jwt
from app.config import settings


def get_password_hash(password: str) -> str:
    """
    Hashes a plaintext password using bcrypt with automatic salting (12 rounds).
    Bcrypt enforces a 72-byte max length limit.
    """
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against its bcrypt hash.
    Returns True if valid, False otherwise.
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates and digitally signs a JWT access token containing subject (user ID) and expiration.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT token using SECRET_KEY and ALGORITHM.
    Returns payload dictionary if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
