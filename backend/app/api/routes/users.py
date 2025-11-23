"""User-related routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_current_user_id
from app.api.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, BookmarkCreate, BookmarkResponse
from app.db.database import get_db
from app.db.models import User, Bookmark
from app.core.security import issue_token
from app.core.config import settings
import hashlib

router = APIRouter(prefix="/api/users", tags=["users"])


def hash_password(password: str) -> str:
    """Simple password hashing (for demo - use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password hash"""
    return hash_password(plain_password) == hashed_password


@router.post("/register", response_model=TokenResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    이메일과 비밀번호로 새 사용자 회원가입
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name or user_data.email.split('@')[0],
        provider="email",
        provider_id=hashed_pw  # Store hashed password in provider_id for email users
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Issue JWT token
    token = issue_token(sub=str(new_user.id))

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_ttl_min * 60,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    이메일과 비밀번호로 로그인
    """
    # Find user
    user = db.query(User).filter(
        User.email == login_data.email,
        User.provider == "email"
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(login_data.password, user.provider_id):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Issue JWT token
    token = issue_token(sub=str(user.id))

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_ttl_min * 60,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    현재 인증된 사용자 정보 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)


@router.get("/me/bookmarks", response_model=List[BookmarkResponse])
def get_my_bookmarks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 북마크 목록 조회
    """
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
    return [BookmarkResponse.model_validate(b) for b in bookmarks]


@router.post("/me/bookmarks", response_model=BookmarkResponse, status_code=201)
def add_bookmark(
    bookmark_data: BookmarkCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    공연을 북마크에 추가
    """
    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.concert_id == bookmark_data.concert_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already bookmarked")

    # Create bookmark
    bookmark = Bookmark(
        user_id=user_id,
        concert_id=bookmark_data.concert_id,
        concert_name=bookmark_data.concert_name,
        poster_url=bookmark_data.poster_url
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse.model_validate(bookmark)


@router.delete("/me/bookmarks/{concert_id}", status_code=204)
def remove_bookmark(
    concert_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    북마크에서 공연 삭제
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.concert_id == concert_id
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()

    return None
