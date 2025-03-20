from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('uvicorn.error')

class ScrapingStrategy(ABC):
    @abstractmethod
    async def scrape(self) -> list:
        pass

class ChoicesScrapingStrategy(ScrapingStrategy):
    async def scrape(self) -> list:
        logger.info(f"Choices scraping")
        return [f"Choices content {i}" for i in range(3)]
