"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str  # For email/password registration
    provider: str = "email"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    provider: str
    profile_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Bookmark Schemas
class BookmarkCreate(BaseModel):
    concert_id: str
    concert_name: Optional[str] = None
    poster_url: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    concert_id: str
    concert_name: Optional[str]
    poster_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Review Schemas
class ReviewCreate(BaseModel):
    concert_id: str
    rating: int  # 1-5
    content: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    concert_id: str
    rating: int
    content: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Token Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
