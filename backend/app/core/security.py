from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Header

from app.core.config import settings


def issue_token(aud: str = "fys-frontend", sub: str = "anon") -> str:
    """Issue a JWT token for authentication"""
    now = datetime.now(timezone.utc)
    payload = {
        "iss": "findyourstage-backend",
        "sub": sub,
        "aud": aud,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_ttl_min)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def verify_bearer(authorization: Optional[str] = Header(None)):
    """Verify Bearer token from Authorization header"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()

    try:
        jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
            audience="fys-frontend"
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return True


def decode_token(token: str) -> dict:
    """Decode and return JWT payload (for OAuth flows)"""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
            audience="fys-frontend"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token decode failed: {e}")
