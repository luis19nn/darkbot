from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('uvicorn.error')

class EditingStrategy(ABC):
    @abstractmethod
    async def edit(self, content):
        pass

class ChoicesEditingStrategy(EditingStrategy):
    async def edit(self, content):
        logger.info("Editing fake video")
        return "fake_video.mp4"
