"""Security utilities for JWT and password handling."""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from backend.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_jwt_token(user_id: int, email: str, role: str) -> str:
    """Create a JWT token."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token_and_get_user(token: str) -> Optional[dict]:
    """Verify token and return user info."""
    payload = decode_jwt_token(token)
    if not payload:
        return None
    return {
        "user_id": int(payload.get("sub")),
        "email": payload.get("email"),
        "role": payload.get("role")
    }
