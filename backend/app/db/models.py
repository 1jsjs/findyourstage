"""Database models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100))
    provider = Column(String(20))  # 'google', 'kakao', 'email'
    provider_id = Column(String(255))  # OAuth provider's user ID
    profile_image = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', provider='{self.provider}')>"


class Bookmark(Base):
    """Bookmark model for saved concerts"""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concert_id = Column(String(50), nullable=False, index=True)  # KOPIS mt20id
    concert_name = Column(String(200))
    poster_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Ensure a user can only bookmark a concert once
    __table_args__ = (
        UniqueConstraint('user_id', 'concert_id', name='uq_user_concert'),
    )

    # Relationships
    user = relationship("User", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark(user_id={self.user_id}, concert_id='{self.concert_id}')>"


class Review(Base):
    """Review model for concert reviews and ratings"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concert_id = Column(String(50), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Rating must be between 1 and 5
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    # Relationships
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review(user_id={self.user_id}, concert_id='{self.concert_id}', rating={self.rating})>"


class Analytics(Base):
    """Analytics model for tracking user events"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'view', 'search', 'bookmark', 'review'
    concert_id = Column(String(50), index=True)
    event_data = Column(JSON)  # Additional event data (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="analytics")

    def __repr__(self):
        return f"<Analytics(event_type='{self.event_type}', concert_id='{self.concert_id}')>"
