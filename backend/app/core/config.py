from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # KOPIS API
    kopis_api_key: str

    # JWT Configuration
    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_ttl_min: int = 10

    # CORS Configuration
    allowed_origins: str = ""
    allowed_origin_regex: str = r"https://.*\.vercel\.app$"

    # Database (optional for now, will be used in step 3)
    database_url: str = ""

    # Redis (optional for now, will be used in step 6)
    redis_url: str = "redis://localhost:6379/0"

    # OAuth (optional for now, will be used in step 5)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    kakao_client_id: str = ""
    kakao_client_secret: str = ""
    kakao_redirect_uri: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_allowed_origins_list(self) -> List[str]:
        """Parse comma-separated allowed origins"""
        if self.allowed_origins:
            return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "https://findyourstage.net",
            "https://www.findyourstage.net",
            "https://findyourstage.vercel.app",
        ]


settings = Settings()
