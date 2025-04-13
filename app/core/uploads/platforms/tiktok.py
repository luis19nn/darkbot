import logging

logger = logging.getLogger('uvicorn.error')

class TikTok:
    async def upload(self, credentials, files):
        logger.info(f"Starting tiktok upload")
        logger.info(f"Files: {files}")
