from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re
from datetime import datetime
from typing import Dict, Any

from scraper_base import BaseScraper

class EtsySearchScraper(BaseScraper):
    """Scrapes Etsy search results for given keywords"""
    
    def __init__(self):
        super().__init__("search", "Etsy Search Results Scraper")
    
    def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape Etsy search results for a given keyword"""
        keyword = params.get("keyword")
        max_listings = params.get("max_listings", 20)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # headless=True for production
            page = browser.new_page()
            stealth_sync(page)  # Apply stealth measures
            
            # Go to Etsy search page
            search_url = f"https://www.etsy.com/search?q={keyword.replace(' ', '+')}"
            page.goto(search_url)
            
            # Wait for page to load
            page.wait_for_timeout(5000)

            # Accept cookies if popup appears
            try:
                page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass  # If popup not found, skip

            # Extract total results count
            total_results = 0
            try:
                # Look for results count text (e.g., "1,234 results")
                results_text = page.locator("[data-testid='search-results-count']").inner_text()
                # Extract number from text like "1,234 results"
                numbers = re.findall(r'[\d,]+', results_text)
                if numbers:
                    total_results = int(numbers[0].replace(',', ''))
            except Exception as e:
                print(f"Could not extract total results: {e}")

            # Wait for listings to load
            page.wait_for_selector("ul li[data-listing-id]", timeout=10000)

            # Scrape results
            items = page.query_selector_all("li[data-listing-id]")
            results = []
            for item in items[:max_listings]:  # Get specified number of listings
                try:
                    title_elem = item.query_selector("h3")
                    price_elem = item.query_selector("[data-buy-box-region='price']")
                    shop_elem = item.query_selector("p.text-gray-lighter")
                    link_elem = item.query_selector("a")
                    
                    if title_elem and price_elem and shop_elem and link_elem:
                        title = title_elem.inner_text().strip()
                        price = price_elem.inner_text().strip()
                        shop = shop_elem.inner_text().strip()
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
                            "shop": shop,
                            "url": link,
                            "scraped_at": datetime.now().isoformat()
                        })
                except Exception as e:
                    continue  # Skip any items with missing data

            browser.close()
            
            return {
                "scraper_id": self.scraper_id,
                "keyword": keyword,
                "total_results": total_results,
                "listings": results,
                "scraped_at": datetime.now().isoformat(),
                "success": True
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
        print(f"Starting Etsy search scrape for keyword: '{params['keyword']}'")
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Hook called after scraping completes"""
        if result.get("success"):
            print(f"Completed Etsy search scrape: {result.get('total_results', 0)} total results, {len(result.get('listings', []))} listings scraped")
        else:
            print(f"Etsy search scrape failed: {result.get('error', 'Unknown error')}") 