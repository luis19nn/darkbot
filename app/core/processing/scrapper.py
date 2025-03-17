from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class Scraper:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized scraper with strategy: {type(strategy).__name__}")

    async def execute(self, source: str):
        logger.info("Starting scraping process")
        content = await self.strategy.scrape(source)
        logger.success(f"Scraped {len(content)} items")
        return content
