import json
import os
import uuid
from pathlib import Path
from datetime import datetime
# import pandas as pd
from typing import Dict, Any
import time
import csv

def update_job_status(job_id: str, status: str, details: Dict[str, Any] = None):
    """Update job status in DynamoDB"""
    import boto3
    DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'dummy-table')
    dynamodb = boto3.resource('dynamodb')
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

def setup_driver():
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    """Initialize undetected ChromeDriver with standard selenium."""
    try:
        # Get Chrome version
        chrome_version = os.popen('google-chrome --version').read().strip().split()[-1].split('.')[0]
        print(f"Detected Chrome version: {chrome_version}")
        # Basic Chrome options
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        # Lambda-specific options
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
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # Initialize ChromeDriver with undetected-chromedriver and standard selenium
        driver = uc.Chrome(
            options=chrome_options,
            version_main=int(chrome_version)
        )
        print("ChromeDriver initialized successfully")
        return driver
    except Exception as e:
        print(f"Error initializing ChromeDriver: {str(e)}")
        raise

def scrape_etsy(keyword: str):
    import pandas as pd
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    driver = None
    try:
        driver = setup_driver()
        url = f"https://www.etsy.com/search?q={keyword}"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wt-grid"))
        )
        products = []
        items = driver.find_elements(By.CLASS_NAME, "wt-grid__item-xs-6")
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, "wt-text-caption").text
                price = item.find_element(By.CLASS_NAME, "wt-price").text
                sales = item.find_element(By.CLASS_NAME, "wt-text-caption").text
                rating = item.find_element(By.CLASS_NAME, "wt-rating__stars").get_attribute("data-rating")
                products.append({
                    'title': title,
                    'price': price,
                    'sales': sales,
                    'rating': rating
                })
            except Exception as e:
                print(f"Error extracting product data: {e}")
                continue
        return pd.DataFrame(products)
    finally:
        if driver:
            driver.quit()

def scrape_dummy(keyword: str, job_id=None):
    """Dummy scrape function that returns hardcoded data for testing a single product page"""
    time.sleep(2)
    dummy_product = {
        'url': 'https://www.etsy.com/listing/123456789/handmade-ceramic-mug',
        'tags': ['ceramic mug', 'handmade', 'pottery', 'kitchen decor', 'coffee cup'],
        'search_terms': ['handmade mug', 'ceramic coffee cup', 'unique kitchen gift', 'pottery mug', 'rustic mug']
    }
    return [dummy_product]

def generate_report(scraped_data, keyword: str) -> str:
    """Generate analysis report from scraped data"""
    report = f"Etsy Keyword Analysis Report for '{keyword}'\n"
    report += "=" * 50 + "\n\n"
    
    # Basic statistics
    report += f"Total products analyzed: {len(df)}\n"
    report += f"Average price: ${df['price'].astype(float).mean():.2f}\n"
    report += f"Average rating: {df['rating'].astype(float).mean():.1f}/5\n\n"
    
    # Top selling products
    report += "Top Selling Products:\n"
    report += "-" * 30 + "\n"
    top_sellers = df.nlargest(5, 'sales')
    for _, row in top_sellers.iterrows():
        report += f"- {row['title']} (${row['price']}, {row['sales']} sales)\n"
    
    # Popular tags
    report += "\nPopular Tags:\n"
    report += "-" * 30 + "\n"
    all_tags = [tag for tags in df['tags'] for tag in tags]
    tag_counts = pd.Series(all_tags).value_counts()
    for tag, count in tag_counts.head(5).items():
        report += f"- {tag}: {count} occurrences\n"
    
    # Related search terms
    report += "\nRelated Search Terms:\n"
    report += "-" * 30 + "\n"
    all_terms = [term for terms in df['search_terms'] for term in terms]
    term_counts = pd.Series(all_terms).value_counts()
    for term, count in term_counts.head(5).items():
        report += f"- {term}: {count} occurrences\n"
    
    return report

def generate_report_no_pandas(scraped_data, job_id):
    """
    take scraped data and write to file
    """
    curr_dir = Path(__file__).parent
    reports_dir = curr_dir / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    csv_path = reports_dir / f'{job_id}_{today_date_str}.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(['URL', 'Tags', 'Related Search Terms'])
        # Write data rows
        for item in scraped_data:
            url = item.get('url', '')
            tags = '; '.join(item.get('tags', []))
            search_terms = '; '.join(item.get('search_terms', []))
            writer.writerow([url, tags, search_terms])
    return csv_path

def lambda_handler(event, context):
    """Lambda function handler"""
    import boto3
    S3_BUCKET = os.environ['S3_BUCKET']
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
    EMAIL_QUEUE_URL = os.environ['EMAIL_QUEUE_URL']
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')
    for record in event['Records']:
        message = json.loads(record['body'])
        job_id = message['job_id']
        report_key = message['report_key']
        keyword = message['keyword']
        update_job_status(job_id, 'STARTED', {'keyword': keyword})
        scraped_data = scrape_dummy(keyword, job_id)
        report_path = generate_report_no_pandas(scraped_data, job_id)
        report_key = f"reports/{job_id}.csv"
        with open(report_path, 'rb') as f:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=report_key,
                Body=f.read()
            )
        sqs.send_message(
            QueueUrl=EMAIL_QUEUE_URL,
            MessageBody=json.dumps({
                'job_id': job_id,
                'report_key': report_key,
                'keyword': keyword,
                'recipient_email': message.get('email', 'user@example.com')
            })
        )
        update_job_status(job_id, 'COMPLETED', {
            'report_key': report_key,
            'products_analyzed': len(scraped_data)
        })
    return {
        'statusCode': 200,
        'body': json.dumps({
            'job_id': job_id,
            'message': 'Analysis started successfully'
        })
    }

if __name__ == "__main__":

  
    # Test the dummy scrape
    keyword = "ceramic mug"
    job_id = "test-job-123"
    scraped_data = scrape_dummy(keyword, job_id)
    print("Scraped Data:", scraped_data)

    # Test the report generation
    report_path = generate_report_no_pandas(scraped_data, job_id)
    print(f"Report generated at: {report_path}")

    # Optionally, print the contents of the generated CSV
    with open(report_path, 'r', encoding='utf-8') as f:
        print("CSV Contents:")
        print(f.read())