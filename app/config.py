from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    APP_ENV: str
    IMG_TMP_DIR: str
    AUDIOS_TMP_DIR: str

    RABBITMQ_URL: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    QUEUE_NAME: str
    PRIORITY: int
    MAX_RETRIES: int
    MAX_CONCURRENT_INSTANCES: int

    DEEPSEEK_API_URL: Optional[str]
    DEEPSEEK_API_KEY: Optional[str]

    PINTEREST_ACCESS_TOKEN: Optional[str]
    PINTEREST_API_URL: Optional[str]

    PEXELS_API_KEY: Optional[str]

    GOOGLE_PROJECT_TYPE: Optional[str]
    GOOGLE_PROJECT_ID: Optional[str]
    GOOGLE_PRIVATE_KEY_ID: Optional[str]
    GOOGLE_PRIVATE_KEY: Optional[str]
    GOOGLE_CLIENT_EMAIL: Optional[str]
    GOOGLE_CLIENT_ID: Optional[str]
    GOOGLE_TOKEN_URI: Optional[str]

    TIKTOK_API_KEY: Optional[str]

    class Config:
        env_file = "implementation.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
