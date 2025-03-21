import logging

logger = logging.getLogger('uvicorn.error')

class Uploader:
    def __init__(self, strategy):
        self.strategy = strategy
        logger.debug(f"Initialized upload with strategy: {type(strategy).__name__}")

    async def execute(self, video_path: str, credentials: dict):
        logger.info("Starting upload execute")
        return await self.strategy.upload(video_path, credentials)
