from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger('uvicorn.error')

class UploadBase(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("Configuration initialized", extra={"config": config})

    @abstractmethod
    async def upload(self):
        pass
