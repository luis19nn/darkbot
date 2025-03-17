from abc import ABC, abstractmethod
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class EditingStrategy(ABC):
    @abstractmethod
    async def edit(self, content: list) -> str:
        pass

class FakeEditingStrategy(EditingStrategy):
    async def edit(self, content: list) -> str:
        logger.info("Editing fake video")
        return "fake_video.mp4"
