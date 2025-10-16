from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

from dotenv import load_dotenv
load_dotenv()  # .env 파일을 환경변수로 로드 (로컬 개발용)

import jwt
import requests
import xmltodict
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------
# Config via Environment
# -----------------------------
KOPIS_API_KEY = os.environ.get("KOPIS_API_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALG = os.environ.get("JWT_ALG", "HS256")
JWT_TTL_MIN = int(os.environ.get("JWT_TTL_MIN", "10"))  # default 10 minutes
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()
] or [
    "http://localhost:5173",
    "https://findyourstage.net",
    "https://www.findyourstage.net",
    "https://*.vercel.app",
]

if not KOPIS_API_KEY:
    raise RuntimeError("Missing env: KOPIS_API_KEY")
if not JWT_SECRET:
    raise RuntimeError("Missing env: JWT_SECRET")

# -----------------------------
# App & CORS
# -----------------------------
app = FastAPI(title="FindYourStage Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Simple in-memory rate limit (per IP & route)
# -----------------------------
# Token endpoint: 10 req / 60s / IP
# Concerts endpoint: 50 req / 60s / IP
RATE_LIMITS = {
    "/api/token": (10, 60),
    "/api/concerts": (50, 60),
}
rate_table: Dict[str, List[float]] = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    path = request.url.path
    limit_cfg = RATE_LIMITS.get(path)
    if not limit_cfg:
        return await call_next(request)

    max_req, window = limit_cfg
    ip = request.client.host if request.client else "unknown"
    key = f"{path}:{ip}"
    now = time.time()
    window_start = now - window
    timestamps = rate_table.get(key, [])
    # drop old
    timestamps = [t for t in timestamps if t >= window_start]
    if len(timestamps) >= max_req:
        raise HTTPException(status_code=429, detail="Too many requests")
    timestamps.append(now)
    rate_table[key] = timestamps
    return await call_next(request)

# -----------------------------
# JWT helpers
# -----------------------------
def issue_token(aud: str = "fys-frontend", sub: str = "anon") -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": "findyourstage-backend",
        "sub": sub,
        "aud": aud,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def verify_bearer(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], audience="fys-frontend")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return True

# -----------------------------
# Routes
# -----------------------------
@app.post("/api/token")
def get_token():
    return {"token": issue_token(), "expires_in": JWT_TTL_MIN * 60}

@app.get("/api/health")
def health():
    return {"ok": True, "message": "Backend running successfully"}

@app.get("/api/concerts")
def concerts(
    stdate: str,
    eddate: str,
    cpage: int = 1,
    rows: int = 20,
    _: bool = Depends(verify_bearer),
):
    """
    Proxies KOPIS '공연목록' and forces 대중음악 (CCCD).
    Dates are YYYYMMDD strings. Returns parsed XML as JSON.

    Query:
      stdate: 시작일 (YYYYMMDD)
      eddate: 종료일 (YYYYMMDD)
      cpage: 페이지
      rows: 페이지당 행 수
    """
    # CCCD = 대중음악
    shcate = "CCCD"

    # KOPIS 공연목록 API
    url = "http://www.kopis.or.kr/openApi/restful/pblprfr"
    params = {
        "service": KOPIS_API_KEY,
        "stdate": stdate,
        "eddate": eddate,
        "cpage": str(cpage),
        "rows": str(rows),
        "shcate": shcate,
    }

    try:
        r = requests.get(url, params=params, timeout=15)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"KOPIS request failed: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"KOPIS upstream {r.status_code}")

    try:
        parsed = xmltodict.parse(r.text)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to parse KOPIS XML")

    # KOPIS: dbs > db [] or single dict
    dbs = parsed.get("dbs", {})
    items = dbs.get("db", [])
    if isinstance(items, dict):
        items = [items]  # single item case

    normalized = [
        {
            "mt20id": it.get("mt20id"),
            "prfnm": it.get("prfnm"),
            "prfpdfrom": it.get("prfpdfrom"),
            "prfpdto": it.get("prfpdto"),
            "fcltynm": it.get("fcltynm"),
            "poster": it.get("poster"),
            "genrenm": it.get("genrenm"),
            "area": it.get("area"),
            "openrun": it.get("openrun"),
        }
        for it in items
    ]

    return {
        "meta": {"cpage": cpage, "rows": rows, "stdate": stdate, "eddate": eddate, "shcate": shcate},
        "raw": parsed,          # XML->JSON 전체
        "items": normalized,    # 프론트 친화 요약
    }
