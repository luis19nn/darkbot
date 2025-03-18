import logging

logger = logging.getLogger('uvicorn.error')

class Editor:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized editor with strategy: {type(strategy).__name__}")

    async def execute(self, content: list):
        logger.info("Starting editor execute")
        return await self.strategy.edit(content)
