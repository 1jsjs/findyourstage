"""Authentication routes"""

from fastapi import APIRouter

from app.core.security import issue_token
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/token")
def get_token():
    """
    JWT 인증 토큰 발급

    이 엔드포인트는 IP당 분당 10회로 요청이 제한됩니다.
    토큰은 설정된 TTL 이후 만료됩니다 (기본값: 10분).
    """
    return {
        "token": issue_token(),
        "expires_in": settings.jwt_ttl_min * 60
    }


@router.get("/health")
def health():
    """서버 상태 확인"""
    return {
        "ok": True,
        "message": "Backend running successfully"
    }
