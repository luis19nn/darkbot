from pathlib import Path
from app.config import settings
from app.core.uploads.base.upload import UploadBase
from app.core.uploads.platforms import ( 
    TikTok, 
    YouTube,
    Instagram
)
import logging

logger = logging.getLogger('uvicorn.error')

class UploadInstance(UploadBase):
    def __init__(self, instance_number: int, config: dict):
        logger.info("Upload instance created")
        self.instance_number = instance_number
        self.config = config
        self.platforms = {
            "tiktok": TikTok(),
            "youtube": YouTube(),
            "instagram": Instagram()
        }

    async def upload(self):
        try:
            logger.info("Starting upload...")

            instance_config = self.config["instances"][self.instance_number]
            accounts = instance_config.get("account", [])
            credentials = instance_config.get("credentials", {})

            if not any(platform in credentials for platform in self.platforms):
                return {"status": "error", "message": "No credentials found for this instance."}

            dir = Path(settings.VIDEOS_TMP_DIR)
            matched_files = set()

            for account in accounts:
                for file in dir.iterdir():
                    if file.is_file():
                        if account in file.name or file.name == account:
                            matched_files.add(str(file.resolve()))

            files = list(matched_files)

            if not files:
                logger.warning(f"No files found for accounts: {accounts}")
                return {"status": "error", "message": "No files found to upload."}

            for platform_name, platform_obj in self.platforms.items():
                cred = credentials.get(platform_name)
                if cred:
                    await platform_obj.upload(cred, files)
                    logger.info(f"Upload for {platform_name} completed successfully.")
                else:
                    logger.info(f"No credentials for {platform_name}, skipping upload.")

            logger.info("Pipeline completed successfully")
            return {"status": "success", "message": "ok"}

        except Exception as e:
            logger.error("Upload failed", extra={"error": str(e), "config": self.config})
            return {"status": "error", "message": str(e)}
