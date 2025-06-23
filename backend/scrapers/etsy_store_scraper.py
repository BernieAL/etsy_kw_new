from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse

from scraper_base import BaseScraper

class EtsyStoreScraper(BaseScraper):
    """Scrapes individual Etsy store pages"""
    
    def __init__(self):
        super().__init__("store", "Etsy Store Scraper")
    
    def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape an Etsy store page"""
        store_url = params.get("store_url")
        max_listings = params.get("max_listings", 20)
        
        # Extract store name from URL
        store_name = self._extract_store_name(store_url)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            stealth_sync(page)
            
            # Go to store page
            page.goto(store_url)
            page.wait_for_timeout(5000)

            # Accept cookies if popup appears
            try:
                page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass

            # Extract store information
            store_info = self._extract_store_info(page)
            
            # Wait for listings to load
            try:
                page.wait_for_selector("ul li[data-listing-id]", timeout=10000)
            except:
                # If no listings found, return store info only
                browser.close()
                return {
                    "scraper_id": self.scraper_id,
                    "store_url": store_url,
                    "store_name": store_name,
                    "store_info": store_info,
                    "total_listings": 0,
                    "listings": [],
                    "scraped_at": datetime.now().isoformat(),
                    "success": True
                }

            # Scrape store listings
            items = page.query_selector_all("ul li[data-listing-id]")
            results = []
            
            for item in items[:max_listings]:
                try:
                    title_elem = item.query_selector("h3")
                    price_elem = item.query_selector("[data-buy-box-region='price']")
                    link_elem = item.query_selector("a")
                    
                    if title_elem and price_elem and link_elem:
                        title = title_elem.inner_text().strip()
                        price = price_elem.inner_text().strip()
                        link = link_elem.get_attribute("href")
                        
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
                except Exception as e:
                    continue

            browser.close()
            
            return {
                "scraper_id": self.scraper_id,
                "store_url": store_url,
                "store_name": store_name,
                "store_info": store_info,
                "total_listings": len(results),
                "listings": results,
                "scraped_at": datetime.now().isoformat(),
                "success": True
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
    
    def _extract_store_info(self, page) -> Dict[str, Any]:
        """Extract store information from the page"""
        store_info = {}
        
        try:
            # Try to extract store description
            desc_elem = page.query_selector("[data-testid='shop-description']")
            if desc_elem:
                store_info["description"] = desc_elem.inner_text().strip()
            
            # Try to extract location
            location_elem = page.query_selector("[data-testid='shop-location']")
            if location_elem:
                store_info["location"] = location_elem.inner_text().strip()
            
            # Try to extract shop stats
            stats_elements = page.query_selector_all("[data-testid*='shop-stats']")
            for elem in stats_elements:
                text = elem.inner_text().strip()
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
        print(f"Starting Etsy store scrape for: {store_name}")
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Hook called after scraping completes"""
        if result.get("success"):
            print(f"Completed Etsy store scrape: {result.get('store_name', 'Unknown')} - {result.get('total_listings', 0)} listings")
        else:
            print(f"Etsy store scrape failed: {result.get('error', 'Unknown error')}") 