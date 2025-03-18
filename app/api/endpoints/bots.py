from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.core.bots.factories.bot_factory import BotFactory
from app.models.schemas import BotStartRequest
from app.workers.tasks import start_bot_instances
import logging

router = APIRouter(prefix="/bots", tags=["bots"])
logger = logging.getLogger('uvicorn.error')

@router.post("/{bot_type}/start")
async def start_bot(
    bot_type: str,
    request: BotStartRequest,
    background_tasks: BackgroundTasks
):
    try:
        logger.info("Starting video creation...")

        background_tasks.add_task(
            start_bot_instances.send,
            bot_type=bot_type,
            config=request.config,
            instances=request.instances
        )

        return {
            "status": "queued",
            "message": "Instances queued for processing",
            "bot_type": bot_type,
            "instances": request.instances
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "invalid_bot_type",
                "msg": str(e),
                "supported_bots": BotFactory.get_available_bots()
            }
        )

    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"type": "server_error", "msg": str(e)}
        )
