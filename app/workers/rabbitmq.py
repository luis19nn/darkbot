from app.config import settings
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import Middleware

class RetryMiddleware(Middleware):
    def after_process_message(self, broker, message, *, result=None, exception=None):
        if exception and message.retries >= message.options.get("max_retries", settings.MAX_RETRIES):
            print(f"Moving message {message.message_id} to DLQ")
            broker.dead_letter(message)

broker = RabbitmqBroker(
    url=settings.RABBITMQ_URL,
    options={
        "exchange_name": settings.EXCHANGE_NAME,
        "exchange_type": settings.EXCHANGE_TYPE,
        "queue_name": settings.MAIN_QUEUE_NAME,
        "queue_args": {
            "x-dead-letter-exchange": settings.DLQ_EXCHANGE,
            "x-dead-letter-routing-key": settings.DLQ_QUEUE_NAME,
            "x-max-priority": settings.DQL_PRIORITY
        }
    }
)

broker.add_middleware(RetryMiddleware())

dramatiq.set_broker(broker)
