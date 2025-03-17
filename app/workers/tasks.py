import dramatiq
from app.config import settings
from app.core.bots.factories.bot_factory import BotFactory
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

@dramatiq.actor(
    queue_name=settings.MAIN_QUEUE_NAME,
    max_retries=settings.MAX_RETRIES,
    retry_when=lambda e: isinstance(e, Exception),
    priority=settings.PRIORITY
)
def start_bot_instances(bot_type: str, config: dict, instances: int):
    try:
        logger.info(f"Starting {instances} instances of bot {bot_type}")

        bot = BotFactory.create(bot_type, config)
        
        for _ in range(instances):
            instance = bot.create_instance()
            result = instance.run_pipeline()
            logger.info(f"Instance result: {result}")

    except Exception as e:
        logger.error(f"Error processing bot {bot_type}: {str(e)}", exc_info=True)
        raise
