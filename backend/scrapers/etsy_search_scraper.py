from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import re
import os
from datetime import datetime
from typing import Dict, Any
import random
import logging
from urllib.parse import quote_plus

from scraper_base import BaseScraper

logger = logging.getLogger("etsy_search_scraper")

class EtsySearchScraper(BaseScraper):
    """Scrapes Etsy search results for given keywords"""
    
    def __init__(self):
        super().__init__("search", "Etsy Search Results Scraper")
    
    async def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape Etsy search results for a given keyword"""
        keyword = params.get("keyword")
        max_listings = params.get("max_listings", 20)
        
        # Get proxy configuration from environment variables or params
        proxy_host = params.get("proxy_host") or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get("proxy_port") or os.getenv("IPROYAL_PROXY_PORT")
        proxy_user = params.get("proxy_user") or os.getenv("IPROYAL_PROXY_USER")
        proxy_pass = params.get("proxy_pass") or os.getenv("IPROYAL_PROXY_PASS")
        
        async with async_playwright() as p:
            # Configure browser launch arguments to match Selenium setup
            browser_args = [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions-except',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            browser = await p.chromium.launch(
                headless=True,  # headless=True for production
                args=browser_args
            )
            
            # Create browser context with proxy configuration and user agent
            context_options = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
            
            if proxy_host and proxy_port:
                # Always set proxy in context if host and port are provided
                proxy_config = {
                    'server': f'http://{proxy_host}:{proxy_port}'
                }
                
                # Add authentication if credentials are provided
                if proxy_user and proxy_pass:
                    proxy_config['username'] = proxy_user
                    proxy_config['password'] = proxy_pass
                
                context_options['proxy'] = proxy_config
                logger.info(f"Using proxy: {proxy_host}:{proxy_port}")
            else:
                logger.warning("No proxy configuration found - using direct connection")
            
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            # Apply stealth measures (similar to selenium-stealth)
            await stealth_async(page)
            
            # Set additional properties to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                window.chrome = {
                    runtime: {},
                };
            """)
            
            # Go to Etsy search page
            encoded_keyword = quote_plus(keyword)
            dd_referrer = "https://www.etsy.com/"
            search_url = f"https://www.etsy.com/search?q={encoded_keyword}&ref=search_bar&dd_referrer=https%3A%2F%2Fwww.etsy.com%2F"
            # Set Referer header to match dd_referrer
            context_options['extra_http_headers']['Referer'] = dd_referrer
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for page to load (matching Selenium timing)
            await page.wait_for_timeout(3000)
            # Throttle: wait an additional 2-4 seconds after page load
            await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))

            # Debug: Take a screenshot to see what we're getting
            try:
                await page.screenshot(path="/app/debug_screenshot.png")
                logger.info(f"Screenshot saved to /app/debug_screenshot.png")
            except Exception as e:
                logger.error(f"Could not take screenshot: {e}")

            # Debug: Get page title and URL
            try:
                page_title = await page.title()
                current_url = page.url
                logger.info(f"Page title: {page_title}")
                logger.info(f"Current URL: {current_url}")
            except Exception as e:
                logger.error(f"Could not get page info: {e}")

            # Debug: Get page content
            try:
                page_content = await page.content()
                logger.info(f"Page content length: {len(page_content)} characters")
                
                # Check if page is too short (likely blocked)
                if len(page_content) < 5000:
                    logger.warning("WARNING: Page content is very short, likely blocked")
                    return {
                        "scraper_id": self.scraper_id,
                        "keyword": keyword,
                        "total_results": 0,
                        "listings": [],
                        "scraped_at": datetime.now().isoformat(),
                        "success": False,
                        "error": "Etsy appears to be blocking the request. Page content is too short. Try using a proxy or different user agent.",
                        "proxy_used": proxy_host is not None,
                        "data_optimized": True,
                        "blocked": True
                    }
                
                if "captcha" in page_content.lower() or "blocked" in page_content.lower():
                    logger.warning("WARNING: Page appears to be blocked or showing captcha")
                    return {
                        "scraper_id": self.scraper_id,
                        "keyword": keyword,
                        "total_results": 0,
                        "listings": [],
                        "scraped_at": datetime.now().isoformat(),
                        "success": False,
                        "error": "Etsy appears to be blocking the request. Try using a proxy or different user agent.",
                        "proxy_used": proxy_host is not None,
                        "data_optimized": True,
                        "blocked": True
                    }
            except Exception as e:
                logger.error(f"Could not get page content: {e}")

            # Accept cookies if popup appears
            try:
                await page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass  # If popup not found, skip

            # Extract total results count
            total_results = 0
            try:
                # Try multiple selectors for results count
                selectors = [
                    "[data-testid='search-results-count']",
                    ".wt-text-caption",
                    "[data-listing-id]",
                    "h1",
                    "body"
                ]
                
                results_text = ""
                for selector in selectors:
                    try:
                        element = await page.locator(selector).first
                        if element:
                            results_text = await element.inner_text()
                            if results_text:
                                break
                    except:
                        continue
                
                # Extract number from text like "1,234 results" or just count listings
                if results_text:
                    numbers = re.findall(r'[\d,]+', results_text)
                    if numbers:
                        total_results = int(numbers[0].replace(',', ''))
                
                # Fallback: count actual listings if we can't get total
                if total_results == 0:
                    items = await page.query_selector_all("li[data-listing-id]")
                    total_results = len(items)
                    
            except Exception as e:
                logger.error(f"Could not extract total results: {e}")
                # Fallback: just count what we can find
                try:
                    items = await page.query_selector_all("li[data-listing-id]")
                    total_results = len(items)
                except:
                    total_results = 0

            # Wait for listings to load (with shorter timeout and fallback)
            try:
                await page.wait_for_selector("ul li[data-listing-id]", timeout=15000)
            except:
                # If timeout, try to find any listings anyway
                logger.warning("Timeout waiting for listings, trying to scrape what's available")

            # Scrape results
            items = await page.query_selector_all("li[data-listing-id]")
            results = []
            
            if not items:
                # Try alternative selectors
                items = await page.query_selector_all("li")
                logger.info(f"Using fallback selector, found {len(items)} items")
            
            for item in items[:max_listings]:  # Get specified number of listings
                try:
                    # Try multiple selectors for each element
                    title_elem = await item.query_selector("h3") or await item.query_selector("h2") or await item.query_selector("a")
                    price_elem = await item.query_selector("[data-buy-box-region='price']") or await item.query_selector(".currency-value") or await item.query_selector("[class*='price']")
                    shop_elem = await item.query_selector("p.text-gray-lighter") or await item.query_selector("[class*='shop']") or await item.query_selector("p")
                    link_elem = await item.query_selector("a")
                    
                    if title_elem and link_elem:
                        title = await title_elem.inner_text()
                        title = title.strip()
                        
                        # Get price if available
                        price = "N/A"
                        if price_elem:
                            price = await price_elem.inner_text()
                            price = price.strip()
                        
                        # Get shop if available
                        shop = "Unknown"
                        if shop_elem:
                            shop = await shop_elem.inner_text()
                            shop = shop.strip()
                        
                        link = await link_elem.get_attribute("href")
                        
                        # Extract listing ID from URL
                        listing_id = None
                        if link:
                            listing_match = re.search(r'/listing/(\d+)/', link)
                            if listing_match:
                                listing_id = listing_match.group(1)

                        results.append({
                            "listing_id": listing_id,
                            "title": title,
                            "price": price,
                            "shop": shop,
                            "url": link,
                            "scraped_at": datetime.now().isoformat()
                        })
                        # Throttle: wait 2-4 seconds between each listing scrape
                        await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))
                except Exception as e:
                    logger.error(f"Error scraping item: {e}")
                    continue  # Skip any items with missing data

            await context.close()
            await browser.close()
            
            return {
                "scraper_id": self.scraper_id,
                "keyword": keyword,
                "total_results": total_results,
                "listings": results,
                "scraped_at": datetime.now().isoformat(),
                "success": True,
                "proxy_used": proxy_host is not None,
                "data_optimized": True
            }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate that required parameters are present"""
        return "keyword" in params and params["keyword"] and len(params["keyword"].strip()) > 0
    
    def get_description(self) -> str:
        """Return description of what this scraper does"""
        return "Scrapes Etsy search results for given keywords, extracting listing count, titles, prices, shops, and URLs"
    
    def get_required_params(self) -> list:
        """Return list of required parameters for this scraper"""
        return ["keyword"]
    
    def pre_scrape_hook(self, params: Dict[str, Any]) -> None:
        """Hook called before scraping starts"""
        proxy_info = ""
        proxy_host = params.get('proxy_host') or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get('proxy_port') or os.getenv("IPROYAL_PROXY_PORT")
        if proxy_host and proxy_port:
            proxy_info = f" with proxy: {proxy_host}:{proxy_port}"
        logger.info(f"Starting Etsy search scrape for keyword: '{params['keyword']}'{proxy_info} (data optimized)")
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Hook called after scraping completes"""
        if result.get("success"):
            logger.info(f"Completed Etsy search scrape: {result.get('total_results', 0)} total results, {len(result.get('listings', []))} listings scraped")
        else:
            logger.error(f"Etsy search scrape failed: {result.get('error', 'Unknown error')}")

    async def test_etsy_homepage(self, params: dict = None) -> dict:
        """TEMP: Test if we can load etsy.com homepage with proxy and log everything."""
        import os
        import random
        from datetime import datetime
        params = params or {}
        proxy_host = params.get("proxy_host") or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get("proxy_port") or os.getenv("IPROYAL_PROXY_PORT")
        proxy_user = params.get("proxy_user") or os.getenv("IPROYAL_PROXY_USER")
        proxy_pass = params.get("proxy_pass") or os.getenv("IPROYAL_PROXY_PASS")
        result = {"success": False}
        async with async_playwright() as p:
            browser_args = [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions-except',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            browser = await p.chromium.launch(headless=True, args=browser_args)
            context_options = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
            if proxy_host and proxy_port:
                proxy_config = {'server': f'http://{proxy_host}:{proxy_port}'}
                if proxy_user and proxy_pass:
                    proxy_config['username'] = proxy_user
                    proxy_config['password'] = proxy_pass
                context_options['proxy'] = proxy_config
                logger.info(f"Using proxy: {proxy_host}:{proxy_port}")
            else:
                logger.warning("No proxy configuration found - using direct connection")
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            await stealth_async(page)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            """)
            # Block WebRTC leaks
            await context.grant_permissions([], origin="https://etsy.com")
            await page.add_init_script('''
                Object.defineProperty(navigator, 'mediaDevices', { get: () => undefined });
                if (window.RTCPeerConnection) { window.RTCPeerConnection = undefined; }
                if (window.webkitRTCPeerConnection) { window.webkitRTCPeerConnection = undefined; }
                if (window.top !== window.self) {
                    if (window.RTCPeerConnection) { window.RTCPeerConnection = undefined; }
                    if (window.webkitRTCPeerConnection) { window.webkitRTCPeerConnection = undefined; }
                }
            ''')
            url = "https://www.etsy.com/"
            try:
                logger.info(f"Navigating to {url}")
                await page.goto(url, wait_until='networkidle')
                await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))
                page_title = await page.title()
                current_url = page.url
                page_content = await page.content()
                content_length = len(page_content)
                screenshot_path = f"/app/etsy_homepage_test.png"
                await page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
                logger.info(f"Page title: {page_title}")
                logger.info(f"Current URL: {current_url}")
                logger.info(f"Page content length: {content_length} characters")
                result = {
                    "success": True,
                    "page_title": page_title,
                    "current_url": current_url,
                    "content_length": content_length,
                    "screenshot": screenshot_path,
                    "proxy_used": proxy_host is not None,
                    "proxy_host": proxy_host,
                    "proxy_port": proxy_port,
                    "scraped_at": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.error(f"Error loading Etsy homepage: {e}")
                result = {"success": False, "error": str(e)}
            await context.close()
            await browser.close()
        return result 