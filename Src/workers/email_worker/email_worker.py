import pika, json, redis, os
from common.logger import get_logger
from workers.email_worker.email_builder import send_email_with_report

#redis setup
r = redis.Redis(host='redis', port=6379, decode_responses=True)
logger = get_logger("email_worker")


# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'user')
RABBITMQ_PASS = os.getenv('RABBITMQ_DEFAULT_PASS', 'pass')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

def get_rabbitmq_connection():
    """Create and return a RabbitMQ connection with credentials"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)


#rbmq setup to establish email queue
connection = get_rabbitmq_connection()
channel = connection.channel()
channel.queue_declare(queue="email")


#callback to handle message recieved on queue
def callback(ch, method, properties, body):

    """
    get message of from queue
    load email body into msg

    call send_email function
    if successfull, log success for this job id
    """

    try:
        msg = json.loads(body)
        job_id = msg["job_id"]
        recipient_email = msg["email"]
        report_path = msg["report_path"]
        

        logger.info(f"[job:{job_id}] EmailWorker received job for {recipient_email}")
        r.set(f"job:{job_id}", "emailing")

        success = send_email_with_report(report_path, recipient_email)

        if success:
            r.set(f"job:{job_id}", "done")
            logger.info(f"[job:{job_id}] Email sent successfully")
        else:
            r.set(f"job:{job_id}", "error_email_failed")
            logger.error(f"[job:{job_id}] Failed to send email")

    except Exception as e:
        logger.exception("EmailWorker - error processing job")

logger.info("EmailWorker is listening for jobs...")
channel.basic_consume(queue="email", on_message_callback=callback, auto_ack=True)
channel.start_consuming()
