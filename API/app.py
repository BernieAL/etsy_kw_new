from flask import Flask,request,jsonify, send_from_directory
from flask_cors import CORS
import csv,os,pika,json,redis,uuid


r = redis.Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

@app.route('/health',methods=['GET'])
def health_check():

    return jsonify({'health': 'OK'},200)


# @app.route('/api/scrape',methods=['POST'])
# def scrape():
#     data = request.get('urls',[])
#     urls = data.get('urls',[])

@app.route('/api/push_to_queue',methods=['POST'])
def scrape():
    data = request.get_json()  
    urls = data.get('urls', [])

    #generate id for this job
    job_id = str(uuid.uuid4())

    #set initial job status for this job in redis
    r.set(f"Job:{job_id}","queued")

    # Attach job_id to data payload
    data['job_id'] = job_id

    #push job to queue - selenium worker will pull
    """payload looks like:
        {
            "urls": ["https://google.com", "https://weather.com"],
            "email": "user@example.com",
            "job_id": "a1b2c3d4"
        }
    
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='scrape')
    channel.basic_publish(
       exchange='', 
       routing_key='scrape', 
       body=json.dumps(data)
    )

    connection.close()

    return jsonify({
        "status": "Job queued. Report will be emailed.",
        "job_id": job_id
    })

if __name__ == '__main__':
    app.run(debug=True)