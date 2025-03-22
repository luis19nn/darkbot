import asyncio
import dramatiq
from app.workers import rabbitmq
from app.config import settings
from app.core.bots.factories.bot_factory import BotFactory
import logging

logger = logging.getLogger('uvicorn.error')

async def run_with_concurrency_limit(coroutines, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def wrapper(coro):
        async with semaphore:
            return await coro
            
    return await asyncio.gather(
        *(wrapper(coro) for coro in coroutines),
        return_exceptions=True
    )

@dramatiq.actor(
    queue_name=settings.QUEUE_NAME,
    max_retries=settings.MAX_RETRIES,
    priority=settings.PRIORITY
)
def start_bot_instances(bot_type: str, config: dict, instances: int):
    try:
        logger.info(f"Starting {instances} instances of bot {bot_type}")

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
