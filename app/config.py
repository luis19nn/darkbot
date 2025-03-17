from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    MAIN_QUEUE_NAME: str = "bot_tasks"
    DLQ_QUEUE_NAME: str = "bot_dlq"
    EXCHANGE_NAME: str = "bot_exchange"
    EXCHANGE_TYPE: str = "direct"
    DLQ_EXCHANGE: str = "bot_dlx"
    PRIORITY: int = 5
    DQL_PRIORITY: int = 10
    WORKER_CONCURRENCY: int = 4
    MAX_RETRIES: int = Field(3, gt=0, le=10)
    TIKTOK_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
