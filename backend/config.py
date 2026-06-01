import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./venv/cloudsense.db"

    # Qwen Cloud (DashScope API Key & Model Configuration)
    QWEN_API_KEY: str = "mock_key"
    QWEN_MODEL: str = "qwen-plus"
    QWEN_BASE_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # Alibaba Cloud
    ALIBABA_ACCESS_KEY_ID: str = "mock_id"
    ALIBABA_ACCESS_KEY_SECRET: str = "mock_secret"
    ALIBABA_REGION: str = "us-east-1"

    # GitHub
    GITHUB_TOKEN: str = "mock_github"
    GITHUB_REPO_OWNER: str = "mock_owner"
    GITHUB_REPO_NAME: str = "mock_repo"

    # Toggle Mocks (helpful for hackathon showcase when live creds aren't set)
    USE_MOCKS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate settings
settings = Settings()

# Check if keys are standard mocks to determine if we should fall back to full mock mode
if settings.QWEN_API_KEY == "mock_key" or settings.ALIBABA_ACCESS_KEY_ID == "mock_id":
    settings.USE_MOCKS = True
else:
    settings.USE_MOCKS = False
