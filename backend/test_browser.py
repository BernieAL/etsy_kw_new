from playwright.sync_api import sync_playwright
import time

def test_browser_display():
    with sync_playwright() as p:
        # Launch browser in non-headless mode
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to a simple page
        page.goto("https://bot.sannysoft.com")
        
        print("Browser should be visible on your screen now!")
        print("Waiting 10 seconds for you to see it...")
        
        # Keep browser open for 10 seconds so you can see it
        time.sleep(10)
        
        browser.close()
        print("Browser closed!")

if __name__ == "__main__":
    test_browser_display() 