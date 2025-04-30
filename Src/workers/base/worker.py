from abc import ABC, abstractmethod
import pika
import redis
from common.logger import get_logger

class BaseWorker(ABC):
    def __init__(self, queue_name: str):
        self.logger = get_logger(self.__class__.__name__)
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.redis_client = None

    def connect(self):
        """Establish connections to RabbitMQ and Redis"""
        try:
            # RabbitMQ connection
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    credentials=pika.PlainCredentials('user', 'pass')
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name)

            # Redis connection
            self.redis_client = redis.Redis(
                host='redis',
                port=6379,
                decode_responses=True
            )
            
            self.logger.info(f"Connected to RabbitMQ and Redis")
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise

    @abstractmethod
    def process_message(self, ch, method, properties, body):
        """Process a message from the queue"""
        pass

    def start(self):
        """Start consuming messages"""
        try:
            self.connect()
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.process_message,
                auto_ack=True
            )
            self.logger.info(f"Started consuming from queue: {self.queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            self.logger.error(f"Error in worker: {str(e)}")
            raise
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close() 