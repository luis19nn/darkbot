from abc import ABC, abstractmethod
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class ScrapingStrategy(ABC):
    @abstractmethod
    async def scrape(self, source: str) -> list:
        pass

class FakeScrapingStrategy(ScrapingStrategy):
    async def scrape(self, source: str) -> list:
        logger.info(f"Fake scraping from {source}")
        return [f"Fake content {i}" for i in range(3)]
