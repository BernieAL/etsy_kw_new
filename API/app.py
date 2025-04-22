from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, pika, redis, uuid

from common.logger import get_logger

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

r = redis.Redis(host='redis', port=6379, decode_responses=True)
logger = get_logger("api")

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("[HEALTH] Health check pinged")
    return jsonify({'health': 'OK'}), 200


@app.route('/api/report/<job_id>',methods=['GET'])
def download_report(job_id):

    """
    serves file from backend as a downloadthe wa
    
    """
    filename = f"report-{job_id}.csv"
    directory = "reports"

    filepath = os.path.join(directory,filename)
    if os.path.exists(filepath):
        logger.info(f"[job:{job_id}] API - report download triggered")    
        return send_from_directory(directory,filename, as_attachment=True)

    logger.warning(f"[job:{job_id}] API - Report not found")
    
    return jsonify({"error": "Report not ready or does not exist."}), 404

@app.route('/api/status/<job_id>', methods=['GET'])
def check_status(job_id):

    """
        tells frontend what stage job is in 
        frontend will call this repeatedly to check job status
    
    """
    status = r.get(f"job:{job_id}")
    result = {"job_id": job_id, "status": status or "unknown"}

    report_path = f"reports/report-{job_id}.csv"
    if status == "done" and os.path.exists(report_path):
        result["download_url"] = f"/api/report/{job_id}"

    logger.info(f"[job:{job_id}] API - Status check: {status or 'unknown'}")
    return jsonify(result)


@app.route('/api/push_to_queue', methods=['POST'])
def push_to_queue():
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        email = data.get('email', 'nobody@example.com')

        job_id = str(uuid.uuid4())
        data['job_id'] = job_id

        logger.info(f"[job:{job_id}] API - Received job submission")
        logger.info(f"[job:{job_id}] API - URLs: {urls}")

        # Store initial status in Redis
        r.set(f"job:{job_id}", "queued")

        # Push job to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='scrape')

        channel.basic_publish(
            exchange='',
            routing_key='scrape',
            body=json.dumps(data)
        )
        connection.close()

        logger.info(f"[job:{job_id}] API - Job pushed to queue successfully")
        return jsonify({"status": "Job queued. Report will be emailed.", "job_id": job_id}), 200

    except Exception as e:
        logger.exception("[API] Error pushing job to queue")
        return jsonify({"error": str(e)}), 500
