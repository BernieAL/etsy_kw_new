import json
import os
import boto3
from datetime import datetime
from common.logger import get_logger
from workers.email_worker.email_builder import send_email_with_report

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Get environment variables
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']

logger = get_logger("lambda_email_worker")

def update_job_status(job_id: str, status: str):
    """Update job status in DynamoDB"""
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.update_item(
        Key={'job_id': job_id},
        UpdateExpression='SET #status = :status, updated_at = :updated_at',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': status,
            ':updated_at': datetime.utcnow().isoformat()
        }
    )
    logger.info(f"[job:{job_id}] Status updated to: {status}")

def get_report_from_s3(report_path: str) -> str:
    """Download report from S3"""
    try:
        response = s3.get_object(
            Bucket=S3_BUCKET,
            Key=report_path
        )
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        logger.error(f"Error downloading report from S3: {e}")
        raise

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        # Process SQS message
        for record in event['Records']:
            msg = json.loads(record['body'])
            job_id = msg['job_id']
            recipient_email = msg['email']
            report_path = msg['report_path']
            
            logger.info(f"[job:{job_id}] EmailWorker processing job for {recipient_email}")
            update_job_status(job_id, "emailing")
            
            try:
                # Get report content from S3
                report_content = get_report_from_s3(report_path)
                
                # Send email with report
                success = send_email_with_report(report_content, recipient_email)
                
                if success:
                    update_job_status(job_id, "completed")
                    logger.info(f"[job:{job_id}] Email sent successfully")
                else:
                    update_job_status(job_id, "error_email_failed")
                    logger.error(f"[job:{job_id}] Failed to send email")
                    
            except Exception as e:
                logger.exception(f"[job:{job_id}] Error processing email job")
                update_job_status(job_id, "error_email_failed")
                raise
                
    except Exception as e:
        logger.exception("Error in email worker Lambda")
        raise 