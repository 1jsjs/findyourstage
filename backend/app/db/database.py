"""Database connection and session management"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = None
SessionLocal = None

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database connection"""
    global engine, SessionLocal

    if not settings.database_url:
        # Database not configured yet
        return None

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Test connections before using
        echo=False  # Set to True for SQL query logging
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    return engine


def get_db():
    """
    Dependency to get database session

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in database"""
    if engine is None:
        raise RuntimeError("Database not initialized")

    Base.metadata.create_all(bind=engine)
