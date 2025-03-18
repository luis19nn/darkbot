import logging

logger = logging.getLogger('uvicorn.error')

class Processor:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized processor with strategy: {type(strategy).__name__}")

    async def execute(self, content: list):
        logger.info("Starting processing execute")
        return await self.strategy.process(content)
