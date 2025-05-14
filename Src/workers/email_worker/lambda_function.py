import json
import os
import boto3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Dict, Any

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
S3_BUCKET = os.environ['S3_BUCKET']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
GOOGLE_APP_PW = os.environ['GOOGLE_APP_PW']
GOOGLE_SENDER_EMAIL = os.environ['GOOGLE_SENDER_EMAIL']
EMAIL_QUEUE_URL = os.environ['EMAIL_QUEUE_URL']

def update_job_status(job_id: str, status: str, details: Dict[str, Any] = None):
    """Update job status in DynamoDB"""
    table = dynamodb.Table(DYNAMODB_TABLE)
    timestamp = datetime.utcnow().isoformat()
    
    item = {
        'job_id': job_id,
        'timestamp': timestamp,
        'status': status
    }
    
    if details:
        item['details'] = details
    
    table.put_item(Item=item)

def send_email(to_email: str, subject: str, body: str):
    """Send email using Gmail SMTP"""
    msg = MIMEMultipart()
    msg['From'] = GOOGLE_SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GOOGLE_SENDER_EMAIL, GOOGLE_APP_PW)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def lambda_handler(event, context):
    """Lambda function handler"""
    try:
        # Process SQS message
        for record in event['Records']:
            message = json.loads(record['body'])
            job_id = message['job_id']
            report_key = message['report_key']
            keyword = message['keyword']
            recipient_email = message['recipient_email']
            
            # Update job status
            update_job_status(job_id, 'EMAIL_STARTED')
            
            # Get report from S3
            response = s3.get_object(
                Bucket=S3_BUCKET,
                Key=report_key
            )
            report_content = response['Body'].read().decode('utf-8')
            
            # Send email
            subject = f"Etsy Keyword Analysis Report: {keyword}"
            body = f"""
            Hello,
            
            Your Etsy keyword analysis report for '{keyword}' is ready.
            
            {report_content}
            
            Best regards,
            Etsy Keyword Analyzer
            """
            
            if send_email(recipient_email, subject, body):
                update_job_status(job_id, 'EMAIL_SENT', {
                    'recipient': recipient_email,
                    'report_key': report_key
                })
            else:
                update_job_status(job_id, 'EMAIL_FAILED', {
                    'error': 'Failed to send email'
                })
                raise Exception("Failed to send email")
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Email sent successfully'
            })
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        
        # Update job status with error
        if 'job_id' in locals():
            update_job_status(job_id, 'EMAIL_FAILED', {'error': error_message})
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        } 