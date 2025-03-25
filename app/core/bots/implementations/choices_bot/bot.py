from app.core.bots.base.bot import BotFactoryBase, BotInstanceBase
from app.core.bots.processing import ( 
    Scraper, 
    Editor, 
    Uploader 
)
import logging
from .strategies import (
    ChoicesScrapingStrategy,
    ChoicesEditingStrategy,
    TiktokUploadStrategy
)

logger = logging.getLogger('uvicorn.error')

class ChoicesBot(BotFactoryBase):
    def __init__(self, config: dict):
        self.config = config
        self.strategies = {
            "scraping": ChoicesScrapingStrategy(),
            "editing": ChoicesEditingStrategy(),
            "upload": TiktokUploadStrategy(),
        }
        logger.info("ChoicesBot initialized", extra={"config": config})

    def create_instance(self, instance_number: int):
        logger.info("Creating new bot instance...")

        return ChoicesBotInstance(
            instance_number=instance_number,
            config=self.config,
            strategies=self.strategies,
        )

class ChoicesBotInstance(BotInstanceBase):
    def __init__(self, instance_number: int, config: dict, strategies: dict):
        super().__init__(config)
        self.instance_number = instance_number
        self.scraper = Scraper(strategies["scraping"])
        self.editor = Editor(strategies["editing"])
        self.uploader = Uploader(strategies["upload"])
        logger.info("Bot instance created")

    async def run_pipeline(self):
        try:
            logger.info("Starting pipeline")
            instance_config = self.config["instances"][self.instance_number]

            content = await self.scraper.execute(instance_config)
            video = await self.editor.execute(content)
            result = await self.uploader.execute(
                video, 
                instance_config["credentials"]
            )

            logger.info("Pipeline completed successfully")
            return {"status": "success", "result": result}

        except Exception as e:
            logger.error("Pipeline failed", extra={"error": str(e), "config": self.config})
            return {"status": "error", "message": str(e)}
