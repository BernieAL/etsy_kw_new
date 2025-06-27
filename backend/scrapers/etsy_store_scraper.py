from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import re
import os
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse
import random

from scraper_base import BaseScraper

class EtsyStoreScraper(BaseScraper):
    """Scrapes individual Etsy store pages"""
    
    def __init__(self):
        super().__init__("store", "Etsy Store Scraper")
    
    async def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape an Etsy store page"""
        store_url = params.get("store_url")
        max_listings = params.get("max_listings", 20)
        
        # Get proxy configuration from environment variables or params
        proxy_host = params.get("proxy_host") or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get("proxy_port") or os.getenv("IPROYAL_PROXY_PORT")
        proxy_user = params.get("proxy_user") or os.getenv("IPROYAL_PROXY_USER")
        proxy_pass = params.get("proxy_pass") or os.getenv("IPROYAL_PROXY_PASS")
        
        # Extract store name from URL
        store_name = self._extract_store_name(store_url)
        
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
                headless=True,
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
                print(f"Using proxy: {proxy_host}:{proxy_port}")
            else:
                print("No proxy configuration found - using direct connection")
            
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
            
            # Go to store page
            await page.goto(store_url, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            # Throttle: wait an additional 2-4 seconds after page load
            await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))

            # Accept cookies if popup appears
            try:
                await page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass

            # Extract store information
            store_info = await self._extract_store_info(page)
            
            # Wait for listings to load
            try:
                await page.wait_for_selector("ul li[data-listing-id]", timeout=10000)
            except:
                # If no listings found, return store info only
                await context.close()
                await browser.close()
                return {
                    "scraper_id": self.scraper_id,
                    "store_url": store_url,
                    "store_name": store_name,
                    "store_info": store_info,
                    "total_listings": 0,
                    "listings": [],
                    "scraped_at": datetime.now().isoformat(),
                    "success": True,
                    "proxy_used": proxy_host is not None
                }

            # Scrape store listings
            items = await page.query_selector_all("ul li[data-listing-id]")
            results = []
            
            for item in items[:max_listings]:
                try:
                    title_elem = await item.query_selector("h3")
                    price_elem = await item.query_selector("[data-buy-box-region='price']")
                    link_elem = await item.query_selector("a")
                    
                    if title_elem and price_elem and link_elem:
                        title = await title_elem.inner_text()
                        title = title.strip()
                        price = await price_elem.inner_text()
                        price = price.strip()
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
                            "url": link,
                            "scraped_at": datetime.now().isoformat()
                        })
                        # Throttle: wait 2-4 seconds between each listing scrape
                        await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))
                except Exception as e:
                    continue

            await context.close()
            await browser.close()
            
            return {
                "scraper_id": self.scraper_id,
                "store_url": store_url,
                "store_name": store_name,
                "store_info": store_info,
                "total_listings": len(results),
                "listings": results,
                "scraped_at": datetime.now().isoformat(),
                "success": True,
                "proxy_used": proxy_host is not None
            }
    
    def _extract_store_name(self, store_url: str) -> str:
        """Extract store name from Etsy store URL"""
        try:
            # Extract from URL like https://www.etsy.com/shop/StoreName
            path = urlparse(store_url).path
            store_name = path.split('/')[-1] if path else "Unknown"
            return store_name.replace('-', ' ').title()
        except:
            return "Unknown Store"
    
    async def _extract_store_info(self, page) -> Dict[str, Any]:
        """Extract store information from the page"""
        store_info = {}
        
        try:
            # Try to extract store description
            desc_elem = await page.query_selector("[data-testid='shop-description']")
            if desc_elem:
                description = await desc_elem.inner_text()
                store_info["description"] = description.strip()
            
            # Try to extract location
            location_elem = await page.query_selector("[data-testid='shop-location']")
            if location_elem:
                location = await location_elem.inner_text()
                store_info["location"] = location.strip()
            
            # Try to extract shop stats
            stats_elements = await page.query_selector_all("[data-testid*='shop-stats']")
            for elem in stats_elements:
                text = await elem.inner_text()
                text = text.strip()
                if "sales" in text.lower():
                    store_info["sales"] = text
                elif "favorited" in text.lower():
                    store_info["favorites"] = text
                    
        except Exception as e:
            print(f"Error extracting store info: {e}")
        
        return store_info
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate that required parameters are present"""
        if "store_url" not in params or not params["store_url"]:
            return False
        
        # Validate that it's an Etsy shop URL
        store_url = params["store_url"]
        return "etsy.com/shop/" in store_url or "etsy.com/shop/" in store_url
    
    def get_description(self) -> str:
        """Return description of what this scraper does"""
        return "Scrapes individual Etsy store pages, extracting store information and listings"
    
    def get_required_params(self) -> list:
        """Return list of required parameters for this scraper"""
        return ["store_url"]
    
    def pre_scrape_hook(self, params: Dict[str, Any]) -> None:
        """Hook called before scraping starts"""
        store_name = self._extract_store_name(params["store_url"])
        proxy_info = ""
        proxy_host = params.get('proxy_host') or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get('proxy_port') or os.getenv("IPROYAL_PROXY_PORT")
        if proxy_host and proxy_port:
            proxy_info = f" with proxy: {proxy_host}:{proxy_port}"
        print(f"Starting Etsy store scrape for: {store_name}{proxy_info}")
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Hook called after scraping completes"""
        if result.get("success"):
            print(f"Completed Etsy store scrape: {result.get('store_name', 'Unknown')} - {result.get('total_listings', 0)} listings")
        else:
            print(f"Etsy store scrape failed: {result.get('error', 'Unknown error')}") 