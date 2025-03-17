from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class Processor:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized processor with strategy: {type(strategy).__name__}")

    async def execute(self, content: list):
        logger.info("Starting processing execute")
        return await self.strategy.process(content)
