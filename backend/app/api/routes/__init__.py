"""API routes module"""

from fastapi import APIRouter

from app.api.routes import auth, concerts, users

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(concerts.router)
api_router.include_router(users.router)

__all__ = ["api_router"]
