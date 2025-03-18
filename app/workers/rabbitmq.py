from app.config import settings
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

broker = RabbitmqBroker(url=settings.RABBITMQ_URL)
dramatiq.set_broker(broker)
