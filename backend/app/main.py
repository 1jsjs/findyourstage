"""FindYourStage Backend - Main Application Entry Point"""

import time
from typing import Dict, List

from dotenv import load_dotenv
load_dotenv()  # Load .env for local development

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import api_router
from app.db.database import init_db

# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(
    title="FindYourStage Backend",
    version="1.0.0",
    description="공연 정보 검색 및 추천 서비스 API"
)

# Initialize database
init_db()

# -----------------------------
# CORS Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Rate Limiting Middleware
# -----------------------------
RATE_LIMITS = {
    "/api/token": (10, 60),      # 10 requests / 60 seconds
    "/api/concerts": (50, 60),   # 50 requests / 60 seconds
}
rate_table: Dict[str, List[float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Simple in-memory rate limiting by IP and route"""
    path = request.url.path
    limit_cfg = RATE_LIMITS.get(path)

    if not limit_cfg:
        return await call_next(request)

    max_req, window = limit_cfg
    ip = request.client.host if request.client else "unknown"
    key = f"{path}:{ip}"
    now = time.time()
    window_start = now - window

    # Get timestamps for this key and filter old ones
    timestamps = rate_table.get(key, [])
    timestamps = [t for t in timestamps if t >= window_start]

    if len(timestamps) >= max_req:
        raise HTTPException(status_code=429, detail="Too many requests")

    timestamps.append(now)
    rate_table[key] = timestamps

    return await call_next(request)


# -----------------------------
# Include Routers
# -----------------------------
app.include_router(api_router)


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "FindYourStage Backend",
        "version": "1.0.0",
        "status": "running"
    }
