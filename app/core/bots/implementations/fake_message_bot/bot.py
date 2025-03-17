from app.core.bots.base.bot import BotBase
from app.core.processing import Scraper, Processor, Editor, Uploader
from app.core.utils.logging import get_logger
from app.core.bots.strategies import (
    FakeScrapingStrategy,
    FakeProcessingStrategy,
    FakeEditingStrategy,
    FakeUploadStrategy
)

logger = get_logger(__name__)

class FakeMessageBot(BotBase):
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.strategies = {
            "scraping": FakeScrapingStrategy(),
            "processing": FakeProcessingStrategy(),
            "editing": FakeEditingStrategy(),
            "upload": FakeUploadStrategy(),
        }
        
        logger.info("FakeMessageBot initialized", extra={"config": config})

    def create_instance(self):
        logger.debug("Criando nova instância do bot")

        return FakeMessageBotInstance(
            config=self.config,
            strategies=self.strategies,
        )

class FakeMessageBotInstance(BotBase):
    def __init__(self, config: dict, strategies: dict):
        super().__init__(config)
        
        self.scraper = Scraper(strategies["scraping"])
        self.processor = Processor(strategies["processing"])
        self.editor = Editor(strategies["editing"])
        self.uploader = Uploader(strategies["upload"])
        
        logger.info("Instância do bot criada")

    async def run_pipeline(self):
        try:
            logger.info("Starting pipeline")

            content = await self.scraper.execute(self.config["source"])
            processed = await self.processor.execute(content)
            video = await self.editor.execute(processed)
            result = await self.uploader.execute(video, self.config["credentials"])

            logger.success("Pipeline completed successfully")
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(
                "Pipeline failed", 
                extra={"error": str(e), "config": self.config}
            )
            return {"status": "error", "message": str(e)}
