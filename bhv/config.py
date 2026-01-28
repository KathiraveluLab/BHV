"""Configuration management for BHV application."""
import os
from typing import Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Application settings and configuration."""
    
    # Application
    APP_NAME: str = "BHV"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.environ.get("BHV_SECRET", "change-me-in-production")
    SESSION_MAX_AGE: int = int(os.environ.get("SESSION_MAX_AGE", "86400"))
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./bhv.db")
    DATABASE_POOL_SIZE: int = int(os.environ.get("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.environ.get("DATABASE_MAX_OVERFLOW", "10"))
    
    # Redis/Cache
    REDIS_URL: Optional[str] = os.environ.get("REDIS_URL")
    CACHE_TTL_IMAGES: int = int(os.environ.get("CACHE_TTL_IMAGES", "300"))
    
    # File upload
    MAX_FILE_SIZE: int = int(os.environ.get("MAX_FILE_SIZE", "52428800"))  # 50MB
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "data/images")
    ALLOWED_EXTENSIONS: set = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    # Image processing
    THUMBNAIL_SIZE: tuple = (300, 300)
    IMAGE_QUALITY: int = int(os.environ.get("IMAGE_QUALITY", "85"))
    MAX_IMAGE_DIMENSION: int = int(os.environ.get("MAX_IMAGE_DIMENSION", "4096"))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.environ.get("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_WINDOW: int = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.environ.get("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.environ.get("MAX_PAGE_SIZE", "100"))
    
    # Server
    HOST: str = os.environ.get("HOST", "127.0.0.1")
    PORT: int = int(os.environ.get("PORT", "8000"))
    WORKERS: int = int(os.environ.get("WORKERS", "1"))
    
    def __init__(self):
        """Validate required settings."""
        if self.SECRET_KEY == "change-me-in-production" and not self.DEBUG:
            raise ValueError("BHV_SECRET must be set in production!")
        
        logger.info(f"Settings loaded: {self.APP_NAME} v{self.APP_VERSION}")
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"Settings(app={self.APP_NAME}, db={self.DATABASE_URL}, redis={bool(self.REDIS_URL)})"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
