import logging

logger = logging.getLogger('uvicorn.error')

class Scraper:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.info(f"Initialized scraper with strategy: {type(strategy).__name__}")

    async def execute(self, config):
        logger.info("Starting scraping process")
        content = await self.strategy.scrape(config)
        return content
