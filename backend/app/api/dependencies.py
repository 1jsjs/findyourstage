"""API dependencies for authentication and other shared functionality"""

from typing import Optional
from fastapi import Header, HTTPException

from app.core.security import decode_token


# Re-export for use in routes
__all__ = ["get_current_user_id"]


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Extract and return current user ID from JWT token
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return int(user_id)
