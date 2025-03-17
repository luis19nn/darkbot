from abc import ABC, abstractmethod
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class UploadStrategy(ABC):
    @abstractmethod
    async def upload(self, video_path: str, credentials: dict) -> str:
        pass

class FakeUploadStrategy(UploadStrategy):
    async def upload(self, video_path: str, credentials: dict) -> str:
        logger.info(f"Uploading fake video to {credentials['platform']}")
        return "https://fake.url/video/123"
