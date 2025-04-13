import logging

logger = logging.getLogger('uvicorn.error')

class YouTube:
    async def upload(self, credentials, files):
        logger.info(f"Starting youtube upload")
        logger.info(f"Files: {files}")
