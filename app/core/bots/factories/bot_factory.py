from app.core.bots.base.bot import BotFactoryBase
from app.core.bots.implementations.choices_bot.bot import ChoicesBot

class BotFactory:
    _bots = {
        "choices_bot": ChoicesBot,
    }

    @classmethod
    def create(cls, bot_type: str, config: dict) -> BotFactoryBase:
        if bot_type not in cls._bots:
            raise ValueError(f"Bot type {bot_type} not supported")
        return cls._bots[bot_type](config)

    @classmethod
    def get_available_bots(cls):
        return list(cls._bots.keys())
