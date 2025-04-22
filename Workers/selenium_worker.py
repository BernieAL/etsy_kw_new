import pika
import redis
import json
import time
import os
from datetime import datetime
from common.logger import get_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# class for file operations (dir creation,file creation)
import file_operations


# env var path to output dir - same place for all reports
ROOT_REPORT_OUTPUT_DIR = "path/to/report-output-dir"

logger = get_logger("scraper_worker")


class ScrapeWorker:
    def __init__(self, job: dict):
        self.job = job
        self.job_id = job.get("job_id")
        self.user_id = job.get("user_id")
        self.date = job.get("date", datetime.now().strftime('%Y-%m-%d'))
        self.urls = job.get("urls", [])
        self.driver = None
        self.all_url_data = []
        self.report_builder = file_operations.ReportPathBuilder(
            ROOT_REPORT_OUTPUT_DIR)

    def log_status(self, status):
        key = f"job:{self.job_id}"
        r.set(key, status)
        logger.info(f"[{self.job_id}] STATUS: {status}")

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def scrape(self):

        # for each url, use self.driver to collect tags + terms
        # append to self.all_url_data
        pass

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
        self.report_builder.make_user_subdir(self.user_id)
        self.report_builder.make_date_subdir(self.date)
        self.report_builder.make_report_file(self.job_id)
        self.report_builder.write_file_formatted(self.all_url_data)

    def run(self):
        try:
            self.log_status("starting")
            self.setup_driver()
            self.log_status("scraping")
            self.scrape()
            self.driver.quit()

            self.log_status("generating_report")
            self.generate_report()

            self.log_status("emailing")
            time.sleep(2)

            self.log_status("done")
        except Exception as e:
            self.log_status(f"error: {e}")
            logger.exception(f"[{self.job_id}] Job failed")
