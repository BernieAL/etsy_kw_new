import os
import sys
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from selenium_stealth_base import SeleniumStealthBase
load_dotenv(dotenv_path="/app/.env")

# Load proxy config from environment variables
proxy_host = os.getenv("IPROYAL_PROXY_HOST")
proxy_port = os.getenv("IPROYAL_PROXY_PORT")
proxy_user = os.getenv("IPROYAL_PROXY_USER")
proxy_pass = os.getenv("IPROYAL_PROXY_PASS")

print("=== PROXY CONFIGURATION ===")
print(f"Proxy Host: {proxy_host}")
print(f"Proxy Port: {proxy_port}")
print(f"Proxy User: {proxy_user}")
print(f"Proxy Pass: {'*' * len(proxy_pass) if proxy_pass else 'None'}")

proxy = None
if proxy_host and proxy_port:
    if proxy_user and proxy_pass:
        proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    else:
        proxy = f"http://{proxy_host}:{proxy_port}"
    print(f"✅ Proxy configured: {proxy_host}:{proxy_port}")
else:
    print("❌ No proxy configuration found!")


def test_bot_detection(driver):
    """Test bot detection using bot.sannysoft.com"""
    print("\n=== BOT DETECTION TEST ===")
    print("Testing stealth measures against bot.sannysoft.com...")
    
    try:
        # Navigate to bot detection test site
        driver.get("https://bot.sannysoft.com")
        time.sleep(5)  # Wait for page to load
        
        print(f"Bot test page title: {driver.title}")
        print(f"Bot test page URL: {driver.current_url}")
        
        # Wait for the test results to load
        time.sleep(3)
        
        # Look for test results
        test_results = {}
        
        # Common test result selectors
        result_selectors = [
            ".test-result",
            "[data-test]",
            ".test",
            ".result",
            "div[class*='test']",
            "div[class*='result']"
        ]
        
        for selector in result_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} test result elements with selector: {selector}")
                    for element in elements[:10]:  # Limit to first 10 for readability
                        try:
                            text = element.text.strip()
                            if text and len(text) < 200:  # Avoid very long text
                                print(f"  Test result: {text}")
                        except:
                            continue
                    break
            except:
                continue
        
        # Take a screenshot for manual review
        try:
            screenshot_path = "bot_detection_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"❌ Failed to save screenshot: {e}")
        
        # Check for specific bot detection indicators
        page_source = driver.page_source.lower()
        
        detection_indicators = {
            "webdriver": "webdriver" in page_source,
            "selenium": "selenium" in page_source,
            "automation": "automation" in page_source,
            "bot": "bot" in page_source,
            "headless": "headless" in page_source,
            "chrome-linux": "chrome-linux" in page_source,
            "navigator.webdriver": "navigator.webdriver" in page_source
        }
        
        print("\n🔍 Bot Detection Analysis:")
        for indicator, detected in detection_indicators.items():
            status = "❌ DETECTED" if detected else "✅ NOT DETECTED"
            print(f"  {indicator}: {status}")
        
        # Overall assessment
        detected_count = sum(detection_indicators.values())
        total_tests = len(detection_indicators)
        stealth_score = ((total_tests - detected_count) / total_tests) * 100
        
        print(f"\n🎯 Stealth Score: {stealth_score:.1f}% ({total_tests - detected_count}/{total_tests} tests passed)")
        
        if stealth_score >= 80:
            print("✅ Excellent stealth - Ready for Etsy scraping!")
        elif stealth_score >= 60:
            print("⚠️  Good stealth - May need minor improvements")
        else:
            print("❌ Poor stealth - Needs significant improvements")
        
        return stealth_score
        
    except Exception as e:
        print(f"❌ Error during bot detection test: {e}")
        return 0


def test_proxy_with_requests():
    """Test if the proxy is working with requests library"""
    if not proxy:
        print("❌ No proxy configured for requests test")
        return False
    
    try:
        print("Testing proxy with requests...")
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        ip_info = response.json()
        print(f"✅ Proxy test successful - IP: {ip_info.get('origin', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")
        return False


class EtsySeleniumTest(SeleniumStealthBase):
    def get_driver(self, proxy=None):
        return self.get_stealth_driver(proxy)


def test_ip_with_selenium(driver):
    """Test what IP address Selenium is using"""
    try:
        print("Testing IP address with Selenium...")
        driver.get("https://httpbin.org/ip")
        time.sleep(3)
        
        # Get the IP from the page
        ip_element = driver.find_element(By.TAG_NAME, "pre")
        ip_info = ip_element.text
        print(f"🌐 Selenium IP info: {ip_info}")
        
        # Also test with a different IP check service
        driver.get("https://api.ipify.org")
        time.sleep(2)
        ip_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"🌐 IPify shows: {ip_text}")
        
        return True
    except Exception as e:
        print(f"Error testing IP: {e}")
        return False


def test_etsy_homepage(driver):
    """Test if we can access the Etsy homepage"""
    try:
        print("Testing Etsy homepage...")
        driver.get("https://www.etsy.com")
        
        # Random wait time to appear more human
        time.sleep(random.uniform(3, 7))
        
        print("Homepage title:", driver.title)
        print("Homepage URL:", driver.current_url)
        print("Homepage source length:", len(driver.page_source))
        
        if len(driver.page_source) > 5000:
            print("✅ Homepage loaded successfully")
            return True
        else:
            print("❌ Homepage blocked or minimal content")
            return False
            
    except Exception as e:
        print(f"Error accessing homepage: {e}")
        return False


def etsy_search(keyword, proxy=None):
    tester = EtsySeleniumTest()
    driver = None
    try:
        # Test IP address first
        print("\n=== IP ADDRESS TESTING ===")
        driver = tester.get_driver(proxy)
        
        # Add a longer wait to ensure browser is stable
        time.sleep(5)
        
        test_ip_with_selenium(driver)
        
        # Test bot detection
        stealth_score = test_bot_detection(driver)
        
        # First test the homepage
        homepage_works = test_etsy_homepage(driver)
        
        if not homepage_works:
            print("Cannot access Etsy homepage - trying search anyway...")
        
        # Now try the search
        encoded_keyword = keyword.replace(" ", "+")
        url = f"https://www.etsy.com/search?q={encoded_keyword}&ref=search_bar"
        
        print(f"Loading search: {url}")
        
        # Add error handling for navigation
        try:
            driver.get(url)
        except Exception as e:
            print(f"Error navigating to search URL: {e}")
            # Try to refresh the page
            try:
                driver.refresh()
                time.sleep(3)
            except:
                pass
        
        # Random wait time
        wait_time = random.uniform(8, 15)
        print(f"Waiting {wait_time:.1f} seconds for page to load...")
        time.sleep(wait_time)
        
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        print("Page source length:", len(driver.page_source))
        
        # Print first 500 characters of page source for debugging
        print("Page source preview:")
        print(driver.page_source[:500])
        print("...")
        
        # Simulate scrolling to trigger lazy loading
        print("Simulating scroll to trigger content loading...")
        try:
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
        except Exception as e:
            print(f"Error during scrolling: {e}")
        
        # Try multiple selectors for product listings with longer waits
        selectors_to_try = [
            "[data-listing-id]",
            ".wt-grid__item-xs-6",
            ".wt-card",
            "[data-palette-listing-image]",
            ".wt-text-caption",
            "h3",
            ".wt-text-title-01",
            ".wt-text-body-01",
            "[data-testid='listing-link']",
            ".wt-display-block",
            "a[href*='/listing/']",
            "[data-testid='search-result']",
            ".wt-grid__item",
            ".wt-card__content",
            ".wt-text-truncate",
            ".wt-text-caption",
            ".wt-text-body",
            ".wt-text-title",
            ".wt-text-heading",
            ".wt-text-subtitle",
            ".wt-text-caption",
            ".wt-text-body-01",
            ".wt-text-title-01",
            ".wt-text-heading-01",
            ".wt-text-subtitle-01",
            ".wt-text-caption-01",
            ".wt-text-body-02",
            ".wt-text-title-02",
            ".wt-text-heading-02",
            ".wt-text-subtitle-02",
            ".wt-text-caption-02"
        ]
        
        products_found = False
        for selector in selectors_to_try:
            try:
                print(f"Trying selector: {selector}")
                wait = WebDriverWait(driver, 10)
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if elements:
                    print(f"✅ Found {len(elements)} elements with {selector}")
                    products_found = True
                    
                    # Try to extract some basic info from first few elements
                    for i, element in enumerate(elements[:5]):
                        try:
                            text = element.text.strip()
                            if text:
                                print(f"  Element {i+1}: {text[:100]}...")
                        except:
                            continue
                    
                    break  # Found elements, stop trying other selectors
                else:
                    print(f"❌ No elements found with {selector}")
                    
            except TimeoutException:
                print(f"❌ Timeout waiting for {selector}")
                continue
            except Exception as e:
                print(f"❌ Error with {selector}: {e}")
                continue
        
        if not products_found:
            print("❌ No product elements found with any selector")
        
        return products_found, stealth_score
        
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False, 0
        
    finally:
        print("Cleaning up...")
        if driver:
            try:
                # Add a small delay before closing to ensure all operations are complete
                time.sleep(2)
                driver.quit()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {e}")


if __name__ == "__main__":
    # Set Docker environment variable
    os.environ['RUNNING_IN_DOCKER'] = '1'
    
    # Load .env file
    load_dotenv(dotenv_path="/app/.env")
    
    # Test proxy with requests first
    print("\n=== PROXY TESTING ===")
    test_proxy_with_requests()
    
    # # Run the main test
    # print("\n=== ETSY SELENIUM TEST ===")
    # success, stealth_score = etsy_search("pearl necklace", proxy=proxy)
    
    # print(f"\n=== FINAL RESULTS ===")
    # print(f"Stealth Score: {stealth_score:.1f}%")
    
    # if success:
    #     print("✅ Search completed successfully!")
    # else:
    #     print("❌ Search failed or no products found") 