from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import re
from datetime import datetime

def scrape_etsy(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True is okay too
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
        for item in items[:20]:  # Get first 20 listings for monitoring
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
            "keyword": keyword,
            "total_results": total_results,
            "listings": results,
            "scraped_at": datetime.now().isoformat()
        }

if __name__ == "__main__":
    keyword = "pearl necklace"
    data = scrape_etsy(keyword)
    if data:
        print(f"Keyword: {data['keyword']}")
        print(f"Total Results: {data['total_results']}")
        print(f"Scraped at: {data['scraped_at']}")
        print(f"Listings found: {len(data['listings'])}")
        for i, item in enumerate(data['listings'][:5], start=1):
            print(f"{i}. {item['title']} | {item['price']} | {item['shop']} \n{item['url']}\n")
