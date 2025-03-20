from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('uvicorn.error')

class UploadStrategy(ABC):
    @abstractmethod
    async def upload(self, video_path: str, credentials: dict) -> str:
        pass

class TiktokUploadStrategy(UploadStrategy):
    async def upload(self, video_path: str, credentials: dict) -> str:
        logger.info(f"Uploading fake video to {credentials['platform']}")
        return "https://fake.url/video/123"
