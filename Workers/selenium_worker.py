import pika,redis,json,time,os
from datetime import datetime
from common.logger import get_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import file_operations #class for file operations (dir creation,file creation)

logger = get_logger("scraper_worker")

# redis setup
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# rbmq setup
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='scrape')

def log_status(job_id,status_msg):

    """updates job status in redis for current job
    """
    key = f"job:{job_id}"
    r.set(key,status_msg)
    print(f"[{job_id}] STATUS: {status_msg}")
    logger.info(f"[{job_id}] STATUS: {status_msg}")



"""
we should have seperate scrape functions
depending on what we are retrieving or scraping

the primary focus is to get tags and related searches for a given listing url

if we have data in format of  {
        url: 'etsy123/',
        tags: []
        related_searches: []
    }

first off scraping the data:
    data.tags.append(tag)
    data.related_searches.append(term)

writing to csv
    line = f"{url},{tags},{related_searches}"

"""
def scrape_tags():

    """
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

def scrape_related_search_terms():


    """
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

def handle_scrape(job):


    job_id = job.get("job_id")
    urls = job.get("urls",[])
    
    log_status(job_id,"recieved: job picked up by worker")

    # Mock scrape step
    log_status(job_id, "scraping")
    try:
       

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)

        scraped_data = [
            {
                'url':None,
                'tags':[],
                'related_search_terms':[]
            }
        ]
       

        for url in urls:

            driver.get(url)
            time.sleep(4)


            tags = scrape_tags(driver)
            search_terms = scrape_related_search_terms(driver)

            



            # print(f"[{job_id}] Scraped {url} - Title: {driver.title}")
            # logger.info(f"[job:{job_id}] SCRAPE - Title: {title}")
            

        driver.quit()
    except Exception as e:
        log_status(job_id, f"error during scraping: {str(e)}")
        return

    # Report generation step
    log_status(job_id, "generating_report")
    try:
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/report-{job_id}.csv"
        with open(filename, "w") as f:
            f.write("url,title\n")
            for row in scraped_data:
                f.write(f"{row['url']},{row['title']}\n")
        print(f"[{job_id}] Report written to {filename}")
    except Exception as e:
        log_status(job_id, f"error during report generation: {str(e)}")
        return

    # Mock email step
    log_status(job_id, "emailing")
    time.sleep(2)  # Placeholder

    log_status(job_id, "done")
    print(f"[{job_id}] Job complete!")
    logger.info(f"[job:{job_id}] Job completed")



def callback(ch, method, properties, body):
    try:
        job = json.loads(body)
        job_id = job.get("job_id", "UNKNOWN")
        logger.info(f"[job:{job_id}] Received job from queue")
        handle_scrape(job)
    except Exception as e:
        logger.exception("Error handling job")

logger.info("🟢 Worker started. Waiting for jobs...")
channel.basic_consume(queue='scrape', on_message_callback=callback, auto_ack=True)
channel.start_consuming()