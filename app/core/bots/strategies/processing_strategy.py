from abc import ABC, abstractmethod
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class ProcessingStrategy(ABC):
    @abstractmethod
    async def process(self, content: list) -> list:
        pass

class FakeProcessingStrategy(ProcessingStrategy):
    async def process(self, content: list) -> list:
        logger.info("Processing fake content with AI")
        return [f"Processed {item}" for item in content]
