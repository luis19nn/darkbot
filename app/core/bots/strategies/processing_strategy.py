from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('uvicorn.error')

class ProcessingStrategy(ABC):
    @abstractmethod
    async def process(self, content: list) -> list:
        pass

class ChoicesProcessingStrategy(ProcessingStrategy):
    async def process(self, content: list) -> list:
        logger.info("Processing fake content with AI")
        return [f"Processed {item}" for item in content]
