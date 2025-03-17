from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

class BotBase(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.debug("Configuration initialized", extra={"config": config})

    @abstractmethod
    def create_instance(self):
        pass

    @abstractmethod
    async def run_pipeline(self):
        pass
