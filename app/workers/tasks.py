import asyncio
import dramatiq
from app.utils import run_with_concurrency_limit
from app.utils import validate_config_instances
from app.workers import rabbitmq
from app.config import settings
from app.core.bots.factories.bot_factory import BotFactory
from app.core.uploads.implementations.upload import UploadInstance
import logging

logger = logging.getLogger('uvicorn.error')

@dramatiq.actor(
    queue_name=settings.BOT_QUEUE_NAME,
    max_retries=settings.MAX_RETRIES,
    priority=settings.PRIORITY
)
def start_bot_instances(bot_type: str, config: dict, instances: int):
    try:
        logger.info(f"Starting {instances} instances of bot {bot_type}")
        validate_config_instances(config, instances)

        # Create bot factory and instances
        bot = BotFactory.create(bot_type, config)
        bot_instances = [bot.create_instance(i) for i in range(instances)]
        
        # Prepare coroutines for execution
        coroutines = [instance.run_pipeline() for instance in bot_instances]

        # Execute all pipelines with concurrency control
        results = asyncio.run(
            run_with_concurrency_limit(
                coroutines,
                max_concurrent=settings.MAX_CONCURRENT_INSTANCES
            )
        )

        # Process results and handle errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Instance {i} failed: {str(result)}",
                    exc_info=result
                )
            else:
                logger.info(f"Instance {i} completed. Result: {result}")

    except Exception as e:
        logger.error(
            f"Critical error processing bot {bot_type}: {str(e)}",
            exc_info=True
        )
        raise

@dramatiq.actor(
    queue_name=settings.UPLOAD_QUEUE_NAME,
    max_retries=settings.MAX_RETRIES,
    priority=settings.PRIORITY
)
def start_upload_instances(config: dict, instances: int):
    try:
        logger.info(f"Uploading videos task starting...")
        validate_config_instances(config, instances)

        upload_instances = [UploadInstance(i, config) for i in range(instances)]
        coroutines = [instance.upload() for instance in upload_instances]

        results = asyncio.run(
            run_with_concurrency_limit(
                coroutines,
                settings.MAX_CONCURRENT_INSTANCES
            )
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Instance {i} failed: {result}", exc_info=result)
            else:
                logger.info(f"Instance {i} completed: {result}")

    except Exception as e:
        logger.error(
            f"Critical error uploading videos: {str(e)}",
            exc_info=True
        )
        raise
