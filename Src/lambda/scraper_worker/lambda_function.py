import json
import os
import boto3
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from common.logger import get_logger

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# Get environment variables
SQS_EMAIL_QUEUE_URL = os.environ['SQS_EMAIL_QUEUE_URL']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']

logger = get_logger("lambda_scraper_worker")

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

def setup_chrome_driver():
    """Initialize ChromeDriver for Lambda environment"""
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Use Chrome binary from Lambda layer
    chrome_options.binary_location = '/opt/chrome/chrome'
    
    driver = uc.Chrome(options=chrome_options)
    return driver

def scrape_url(driver, url: str) -> dict:
    """Scrape a single URL and return the data"""
    try:
        driver.get(url)
        time.sleep(2)  # Allow page to load
        
        # Scrape tags
        tags = []
        try:
            tag_elements = driver.find_elements(By.CSS_SELECTOR, '.tag-selector')  # Update selector
            tags = [tag.text for tag in tag_elements]
        except Exception as e:
            logger.warning(f"Failed to scrape tags: {e}")
        
        # Scrape search terms
        search_terms = []
        try:
            term_elements = driver.find_elements(By.CSS_SELECTOR, '.search-term-selector')  # Update selector
            search_terms = [term.text for term in term_elements]
        except Exception as e:
            logger.warning(f"Failed to scrape search terms: {e}")
        
        return {
            'url': url,
            'tags': tags if tags else None,
            'search_terms': search_terms if search_terms else None
        }
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {e}")
        return None

def generate_report(job_id: str, data: list) -> str:
    """Generate CSV report and upload to S3"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/{job_id}_{timestamp}.csv"
    
    # Create CSV content
    csv_content = "URL,Tags,Search Terms\n"
    for item in data:
        tags = ','.join(item['tags']) if item['tags'] else ''
        terms = ','.join(item['search_terms']) if item['search_terms'] else ''
        csv_content += f"{item['url']},{tags},{terms}\n"
    
    # Upload to S3
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=csv_content
    )
    
    return filename

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        # Process SQS message
        for record in event['Records']:
            job = json.loads(record['body'])
            job_id = job['job_id']
            urls = job['urls']
            
            logger.info(f"[job:{job_id}] Processing job with {len(urls)} URLs")
            update_job_status(job_id, "processing")
            
            # Initialize Chrome driver
            driver = setup_chrome_driver()
            
            try:
                # Scrape each URL
                all_url_data = []
                for url in urls:
                    data = scrape_url(driver, url)
                    if data:
                        all_url_data.append(data)
                
                # Generate and upload report
                report_path = generate_report(job_id, all_url_data)
                
                # Send message to email queue
                sqs.send_message(
                    QueueUrl=SQS_EMAIL_QUEUE_URL,
                    MessageBody=json.dumps({
                        'job_id': job_id,
                        'email': job['email'],
                        'report_path': report_path
                    })
                )
                
                update_job_status(job_id, "completed")
                logger.info(f"[job:{job_id}] Job completed successfully")
                
            finally:
                driver.quit()
                
    except Exception as e:
        logger.exception("Error processing job")
        if 'job_id' in locals():
            update_job_status(job_id, "error")
        raise 