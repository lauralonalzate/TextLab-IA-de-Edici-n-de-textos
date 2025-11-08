from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "TextLab API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    # Parse comma-separated string or use list
    # In .env, use: CORS_ORIGINS=http://localhost:3000,https://app.example.com
    CORS_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    STORAGE_PATH: str = "exports"
    
    # AWS S3 (optional, only if using S3 storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_BUCKET_PREFIX: str = "exports/"
    
    # Rate Limiting
    ENABLE_RATE_LIMITING: bool = True
    LOGIN_RATE_LIMIT: int = 5  # requests per minute
    GENERAL_RATE_LIMIT: int = 60  # requests per minute
    
    # Security
    TRUST_PROXY: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

