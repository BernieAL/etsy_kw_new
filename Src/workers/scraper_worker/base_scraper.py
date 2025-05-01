from abc import ABC, abstractmethod
from datetime import datetime
import csv,os

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
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv,find_dotenv


def get_driver(self):

        
        """Initialize Selenium ChromeDriver."""
        uc_chrome_options = uc.ChromeOptions()
        uc_chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        uc_chrome_options.add_argument('--ignore-ssl-errors=yes')
        uc_chrome_options.add_argument('--ignore-certificate-errors')
        uc_chrome_options.add_argument('--allow-running-insecure-content')

        #docker specific options
        if os.getenv('RUNNING_IN_DOCKER') == '1':
            print("Running in Docker - adding container-specific Chrome options")
            uc_chrome_options.add_argument('--headless')
            uc_chrome_options.add_argument('--no-sandbox')
            uc_chrome_options.add_argument('--disable-dev-shm-usage')
            uc_chrome_options.add_argument('--disable-gpu')
            uc_chrome_options.add_argument('--remote-debugging-port=9222')
            uc_chrome_options.add_argument('--window-size=1920,1080')
            uc_chrome_options.add_argument('--disable-setuid-sandbox')
            uc_chrome_options.add_argument('--single-process')

try:
    driver = uc.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=uc_chrome_options
    )
    print("ChromeDriver intialized successfully")
    
    return driver
except Exception as e:
    print(f"Error initializing ChromeDriver: {str(e)}")
    raise