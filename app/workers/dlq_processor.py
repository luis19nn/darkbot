import dramatiq
import time
from app.config import settings
from app.workers.rabbitmq import broker
from app.core.utils.logging import get_logger

logger = get_logger(__name__)

def process_dlq_messages():
    with broker.connection() as conn:
        channel = conn.channel()
        channel.queue_declare(queue=settings.DLQ_QUEUE_NAME, durable=True)
        
        def callback(ch, method, properties, body):
            try:
                message = dramatiq.Message.decode(body)
                logger.info(f"Reprocessing message from DLQ: {message.message_id}")
                
                broker.enqueue(message, queue_name=settings.MAIN_QUEUE_NAME)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Successfully requeued message {message.message_id}")

            except Exception as e:
                logger.error(f"Failed to reprocess message: {str(e)}", exc_info=True)
                time.sleep(5)

        channel.basic_consume(queue=settings.DLQ_QUEUE_NAME, on_message_callback=callback, auto_ack=False)
        logger.info("DLQ Consumer started. Waiting for messages...")
        channel.start_consuming()
