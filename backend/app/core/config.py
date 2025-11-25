from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI backend service"

    API_V1_STR: str = "/api/v1"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database configuration
    # Set DB_TYPE to "postgresql" for local dev, "firestore" for Google Cloud
    DB_TYPE: str = "postgresql"

    # PostgreSQL configuration (for local development)
    POSTGRES_USER: str = "fastapi_user"
    POSTGRES_PASSWORD: str = "fastapi_password"
    POSTGRES_DB: str = "fastapi_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # Firestore configuration (for Google Cloud)
    GCP_PROJECT_ID: Optional[str] = None
    FIRESTORE_COLLECTION: str = "default"

    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL based on DB_TYPE"""
        if self.DB_TYPE == "postgresql":
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return ""

    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Content length limits (configurable)
    MAX_POST_CONTENT_LENGTH: int = 280
    MAX_COMMENT_CONTENT_LENGTH: int = 280

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
