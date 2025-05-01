import pika,redis,json,time,os,sys,csv
from datetime import datetime
from common.logger import get_logger
from common.file_operations import ReportPathBuilder


from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import seleniumwire.undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv,find_dotenv

#ensure project root is accessible
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)




# env var path to output dir - same place for all reports
ROOT_REPORT_OUTPUT_DIR = os.getenv('ROOT_REPORT_OUTPUT_DIR', '/app/reports')

logger = get_logger("scraper_worker")
r = redis.Redis(host='redis', port=6379, decode_responses=True)

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

class ScrapeWorker():
    def __init__(self, job: dict):
        self.job = job
        self.job_id = job.get("job_id")
        self.user_id = job.get("user_id")
        self.user_email = job.get("email")
        self.date = job.get("date", datetime.now().strftime('%Y-%m-%d'))
        self.urls = job.get("urls", [])
        self.driver = None
        self.all_url_data = []
        self.report_builder = ReportPathBuilder(ROOT_REPORT_OUTPUT_DIR)

    def log_status(self, status):
        """Update job status in Redis"""
        r.set(f"job:{self.job_id}", status)
        logger.info(f"[job:{self.job_id}] Status updated to: {status}")


    def setup_driver(self):
        """Initialize Selenium ChromeDriver."""
        try:
            # Get Chrome version
            chrome_version = os.popen('google-chrome --version').read().strip().split()[-1].split('.')[0]
            print(f"Detected Chrome version: {chrome_version}")
            
            # Basic Chrome options
            uc_chrome_options = uc.ChromeOptions()
            uc_chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            uc_chrome_options.add_argument('--ignore-ssl-errors=yes')
            uc_chrome_options.add_argument('--ignore-certificate-errors')
            uc_chrome_options.add_argument('--allow-running-insecure-content')
            
            # Docker-specific options
            if os.getenv('RUNNING_IN_DOCKER') == '1':
                print("Running in Docker - adding container-specific Chrome options")
                uc_chrome_options.add_argument('--headless=new')
                uc_chrome_options.add_argument('--no-sandbox')
                uc_chrome_options.add_argument('--disable-dev-shm-usage')
                uc_chrome_options.add_argument('--disable-gpu')
                uc_chrome_options.add_argument('--window-size=1920,1080')
                uc_chrome_options.add_argument('--disable-setuid-sandbox')
                uc_chrome_options.add_argument('--disable-extensions')
                uc_chrome_options.add_argument('--disable-software-rasterizer')
                uc_chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                uc_chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                uc_chrome_options.add_argument('--remote-debugging-address=0.0.0.0')
                uc_chrome_options.add_argument('--remote-debugging-port=9222')
                uc_chrome_options.add_argument('--disable-web-security')
                uc_chrome_options.add_argument('--allow-running-insecure-content')
                uc_chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Initialize ChromeDriver with ChromeDriverManager
            driver = uc.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=uc_chrome_options,
                version_main=int(chrome_version)
            )
            
            print("ChromeDriver initialized successfully")
            return driver
            
        except Exception as e:
            print(f"Error initializing ChromeDriver: {str(e)}")
            raise

    def scrape_dummy_test(self):

        """
        
        this is a dummy function for testing selenium functionality in a worker
        This will visit bot.sannysoft.com and return some hardcoded dummy data as if a scrape
        at etsy had occured.

        
        """
        dummy_url = 'etsy.com/123'
        dummy_tags = ['kitchen','decor','rustic']
        dummy_search_terms = ['home decor','house warming','home gifts']

        self.all_url_data.append({
            'url':dummy_url,
            'tags': dummy_tags if dummy_tags else None,
            'search_terms': dummy_search_terms if dummy_search_terms else None
        })

        return 
    def scrape(self):

        # for each url, use self.driver to collect tags + terms
        # append to self.all_url_data
        for url in self.urls:
            self.driver.get(url)
            time.sleep(2)

            tags = self.scrape_tags()
            search_terms = self.scrape_related_search_terms()

            self.all_url_data.append({
                'url':url,
                'tags': tags if tags else None,
                'search_terms': search_terms if search_terms else None
            })

    def scrape_tags(self) -> list:
        """
        Locate and return tag elements from the current page using self.driver


            this function will be for targeting tag elements on etsy product page
            for a single URL, and scraping these only, and putting into a list

            will be called once for each URL

            return list of scraped tags on page

            all DOM location logic for tags is here

            failure of this isolated to this process only
        """

        """
            log entry to this process
            try
                locate related tag elements on page
                if found:
                    put in list, return success msg, and populated list
                    log if found
                if not found:
                    throw exception or return fail
                    log if not found
            except
                throw exception if there was an error like element not foud


        """
        tags = []
        try:
            # your tag scraping logic using self.driver
            # tags = [e.text for e in self.driver.find_elements(...)]
            logger.info(f"[{self.job_id}] Tags scraped: {tags}")
        except Exception as e:
            logger.warning(f"[{self.job_id}] Failed to scrape tags: {e}")
        return tags

    def scrape_related_search_terms(self) -> list:
        """

            Locate and return related search term elements from the current page using self.driver

            this function is for targeting releated search term elements on etsy product page for a single URL, and scraping these only, and putting into a list

            will be called once for each URL

            returns list of scraped terms on page

            all DOM location logic for related_search_terms is here

            failure of this isolated to this process only
        
        """   
        """   
            log entry to this process
            try     
                locate realted ssearch term elements on page
                if found:
                    put in list, return success msg, and populated list
                    log if found
                if not found: 
                    throw exception or return fail
                    log if not found
            except
                throw exception if there was an error like element not foud
        
        """
    
        terms = []
        try:
            # terms = [e.text for e in self.driver.find_elements(...)]
            logger.info(f"[{self.job_id}] Related terms scraped: {terms}")
        except Exception as e:
            logger.warning(f"[{self.job_id}] Failed to scrape related terms: {e}")
        return terms
    def generate_report(self):
        
        """
        Generates report using scraped data
        Accesses scraped data through class property -> all_url_data

        Creates subdir for user
        Creates subdir for user/curr_date
        Creates file path to save report to
        Calls function to write data in specified format

        generated report will be stored at report_filepath
        """
        
        #make subdir for user_id
        self.report_builder.make_user_subdir(self.user_id)
        #make subdir for current date
        self.report_builder.make_date_subdir(self.date)
        #make empty report file
        self.report_filepath = self.report_builder.make_report_file(self.job_id)
        self.report_builder.write_file_formatted(self.all_url_data)
        return self.report_filepath

    def push_to_email_queue(self):


        """
        Called AFTER generting report 
        this will push generated report file path to email queue
        -email_worker will be listening for messages on email_queue
        -it will pull the msg, access report using file path, attach to email 
            and send off
        """

        email_payload = {
            "job_id": self.job_id,
            "email": self.user_email,
            "report_path": str(self.report_filepath),
        }

        #establish connection to push email_payload to email queue
        #email worker is listening to email_queue
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue="email")
        channel.basic_publish(
            exchange='',
            routing_key='email',
            body=json.dumps(email_payload)
        )

        logger.info(f"[job:{self.job_id}] Email sent to queue")


    def preview_report_contents(self, report_file_path):
        file = self.report_filepath

        with open(file,'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
        


    def run(self):
        try:
            self.log_status("starting")
            self.setup_driver()
            self.log_status("scraping")
            
            self.scrape_dummy_test()
            # self.scrape()
            # self.driver.quit()

            self.log_status("generating_report")
            self.generate_report()

            

            self.log_status("emailing")
            self.push_to_email_queue()
            time.sleep(2)

            self.log_status("done")
        except Exception as e:
            self.log_status(f"error: {e}")
            logger.exception(f"[{self.job_id}] Job failed")



def process_msg(ch,method,properties,body):

    try:
        job = json.loads(body)
        job_id = job["job_id"]
        recipient_email = job["email"]
        logger.info(f"[job:{job_id}] ScraperWorker received job for {recipient_email}")
     
        
        worker = ScrapeWorker(job)
        worker.log_status("processing")
        
        worker.setup_driver()
        # worker.scrape()
        worker.scrape_dummy_test()
        worker.generate_report()
        
        
        worker.preview_report_contents(worker.report_filepath)
        
        worker.push_to_email_queue()

        worker.log_status("completed")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
            logger.error(f"Error processing job:{e}")
            worker.log_status("failed")
            ch.basic_nack(delivery_tag=method.delivery_tag)

def main():

    """
    Main function set up RBMQ connection and start consuming messages 
    """

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()

            #declare queue
            channel.queue_declare(queue='scrape')

            #set up consumer
            # listen to scrape queue
           
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='scrape',on_message_callback=process_msg)
            
            logger.info("ScraperWorker is listening for jobs...")
            channel.start_consuming()
        
        except pika.exceptions.AMQPConnectionError:
            logger.error("Lost connection to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)



if __name__ == '__main__':
    main()
