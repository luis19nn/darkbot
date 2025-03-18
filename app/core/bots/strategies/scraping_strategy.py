from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('uvicorn.error')

class ScrapingStrategy(ABC):
    @abstractmethod
    async def scrape(self, source: str) -> list:
        pass

class FakeScrapingStrategy(ScrapingStrategy):
    async def scrape(self, source: str) -> list:
        logger.info(f"Fake scraping from {source}")
        return [f"Fake content {i}" for i in range(3)]
