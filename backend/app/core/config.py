"""
Application configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Australian Privacy Act ADM Compliance Framework"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/adm_compliance"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Azure
    AZURE_REGION: str = "australiaeast"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_KEY_VAULT_URL: str = ""

    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB

    # Email/Alerts
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@example.gov.au"
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL_FROM: str = "alerts@example.gov.au"

    # Monitoring
    ENABLE_MONITORING: bool = True
    DRIFT_DETECTION_INTERVAL: int = 86400  # 24 hours
    ALERT_RETENTION_DAYS: int = 90

    # SLA
    REQUEST_SLA_DAYS: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
