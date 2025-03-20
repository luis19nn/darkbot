from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str
    LOG_LEVEL: str
    RABBITMQ_URL: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    QUEUE_NAME: str
    PRIORITY: int
    MAX_RETRIES: int
    MAX_CONCURRENT_INSTANCES: int
    TIKTOK_API_KEY: Optional[str]

    class Config:
        env_file = "implementation.env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
