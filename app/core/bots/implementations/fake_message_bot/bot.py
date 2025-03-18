from app.core.bots.base.bot import BotFactoryBase, BotInstanceBase
from app.core.processing import ( 
    Scraper, 
    Processor, 
    Editor, 
    Uploader 
)
import logging
from app.core.bots.strategies import (
    FakeScrapingStrategy,
    FakeProcessingStrategy,
    FakeEditingStrategy,
    FakeUploadStrategy
)

logger = logging.getLogger('uvicorn.error')

class FakeMessageBot(BotFactoryBase):
    def __init__(self, config: dict):
        self.config = config
        self.strategies = {
            "scraping": FakeScrapingStrategy(),
            "processing": FakeProcessingStrategy(),
            "editing": FakeEditingStrategy(),
            "upload": FakeUploadStrategy(),
        }
        logger.info("FakeMessageBot initialized", extra={"config": config})

    def create_instance(self, credential_number: int):
        logger.debug("Creating new bot instance...")

        return FakeMessageBotInstance(
            credential_number=credential_number,
            config=self.config,
            strategies=self.strategies,
        )

class FakeMessageBotInstance(BotInstanceBase):
    def __init__(self, credential_number: int, config: dict, strategies: dict):
        super().__init__(config)
        self.credential_number = credential_number
        self.scraper = Scraper(strategies["scraping"])
        self.processor = Processor(strategies["processing"])
        self.editor = Editor(strategies["editing"])
        self.uploader = Uploader(strategies["upload"])
        logger.info("Bot instance created")

    async def run_pipeline(self):
        try:
            logger.info("Starting pipeline")

            content = await self.scraper.execute(self.config["source"])
            processed = await self.processor.execute(content)
            video = await self.editor.execute(processed)
            result = await self.uploader.execute(
                video, 
                self.config["credentials"][self.credential_number]
            )

            logger.info("Pipeline completed successfully")
            return {"status": "success", "result": result}

        except Exception as e:
            logger.error("Pipeline failed", extra={"error": str(e), "config": self.config})
            return {"status": "error", "message": str(e)}
