from app.core.bots.implementations.fake_message_bot.bot import FakeMessageBot

class BotFactory:
    _bots = {
        "fake_message": FakeMessageBot,
    }

    @classmethod
    def create(cls, bot_type: str, config: dict):
        if bot_type not in cls._bots:
            raise ValueError(f"Bot type {bot_type} not supported")
        return cls._bots[bot_type](config)
    
    @classmethod
    def get_available_bots(cls):
        return list(cls._bots.keys())
