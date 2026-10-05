"""Application Configuration for AgentAssure.

Centralized settings powered by Pydantic v2 BaseSettings.
All configuration parameters can be overridden via environment variables or .env files.
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for AgentAssure application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core Application Settings
    APP_NAME: str = "AgentAssure"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "agentassure_super_secret_jwt_hmac_key_change_in_production_32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_ALGORITHM: str = "HS256"

    # Database & Storage
    # Default to sqlite:///./agentassure.db if POSTGRES_URL not provided
    DATABASE_URL: str = Field(
        default="sqlite:///./agentassure.db",
        description="Database connection URI (PostgreSQL or SQLite for testing)",
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = True  # Eager fallback for test and standalone mode

    # Smart Sampling Weights
    SAMPLING_WEIGHT_JUDGE_SCORE: float = 0.35
    SAMPLING_WEIGHT_ASR_ERROR: float = 0.25
    SAMPLING_WEIGHT_LOOP_COUNT: float = 0.20
    SAMPLING_WEIGHT_CUSTOMER_DROPOFF: float = 0.10
    SAMPLING_WEIGHT_NEGATIVE_SENTIMENT: float = 0.10

    # Stratified Sampling Percentages
    STRATA_RISK_PERCENT: float = 0.65
    STRATA_NEW_VERSION_PERCENT: float = 0.20
    STRATA_EDGE_CASE_PERCENT: float = 0.15

    # Release Gating Defaults
    CRITICAL_CATEGORIES: List[str] = [
        "Factual Accuracy",
        "Compliance",
        "Prompt Injection & Safety",
    ]
    CRITICAL_PASS_THRESHOLD: float = 0.95
    STANDARD_PASS_THRESHOLD: float = 0.88
    STATISTICAL_ALPHA: float = 0.05

    # Data Retention & Security
    ARCHIVE_RETENTION_DAYS: int = 60
    PURGE_RETENTION_DAYS: int = 90
    DATA_DIR: Path = Path("./data")
    AUDIO_DIR: Path = Path("./data/audio")
    RUBRICS_DIR: Path = Path("./config")

    # Integrations
    OPENAI_API_KEY: str = "mock-openai-key"
    ANTHROPIC_API_KEY: str = "mock-anthropic-key"
    LINEAR_API_KEY: str = "mock-linear-key"
    JIRA_BASE_URL: str = "https://mock-company.atlassian.net"
    JIRA_API_TOKEN: str = "mock-jira-token"
    JIRA_USER_EMAIL: str = "qa-lead@agentassure.internal"
    SLACK_WEBHOOK_URL: str = "https://hooks.slack.com/services/mock/webhook"

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"


settings = Settings()
