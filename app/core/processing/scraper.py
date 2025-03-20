import logging

logger = logging.getLogger('uvicorn.error')

class Scraper:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized scraper with strategy: {type(strategy).__name__}")

    async def execute(self):
        logger.info("Starting scraping process")
        content = await self.strategy.scrape()
        logger.info(f"Scraped {len(content)} items")
        return content
