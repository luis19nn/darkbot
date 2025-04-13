import logging

logger = logging.getLogger('uvicorn.error')

class Instagram:
    async def upload(self, credentials, files):
        logger.info(f"Starting instagram upload")
        logger.info(f"Files: {files}")
