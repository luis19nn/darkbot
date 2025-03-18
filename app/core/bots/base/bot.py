from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger('uvicorn.error')

class BotInstanceBase(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.debug("Configuration initialized", extra={"config": config})

    @abstractmethod
    async def run_pipeline(self):
        pass

class BotFactoryBase(ABC):
    @abstractmethod
    def create_instance(self, credential_number: int) -> BotInstanceBase:
        pass
