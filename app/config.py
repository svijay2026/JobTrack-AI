from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings.
    Loads and validates configuration from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "JobTrack AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database Configuration (MySQL)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "jobtrack_ai"
    SQLALCHEMY_DATABASE_URI: Union[str, None] = None

    # Database Connection Pooling
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600  # Recycle connections every hour
    DB_POOL_PRE_PING: bool = True

    # Security & JWT
    SECRET_KEY: str = "default_secret_key_please_change_in_production_32chars_min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # File Storage
    UPLOAD_DIR: str = "uploads/resumes"
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def database_url(self) -> str:
        """Construct the SQLAlchemy connection string for MySQL using PyMySQL driver."""
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


# Global settings instance
settings = Settings()
