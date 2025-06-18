from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def scrape_etsy(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True is okay too
        page = browser.new_page()
        stealth_sync(page)  # Apply stealth measures
        page.goto("https://bot.sannysoft.com")

        # # Accept cookies if popup appears
        # try:
        #     page.locator("button:has-text('Accept')").click(timeout=3000)
        # except:
        #     pass  # If popup not found, skip

        # # Enter search term and submit
        # search_input = page.locator("input[data-id='search-query']")
        # search_input.fill(keyword)
        # search_input.press("Enter")

        # # Wait for listings to load
        # page.wait_for_selector("ul li[data-listing-id]")

        # # Scrape results
        # items = page.query_selector_all("li[data-listing-id]")
        # results = []
        # for item in items[:10]:  # Get first 10 listings
        #     try:
        #         title = item.query_selector("h3").inner_text().strip()
        #         price = item.query_selector("[data-buy-box-region='price']").inner_text().strip()
        #         shop = item.query_selector("p.text-gray-lighter").inner_text().strip()
        #         link = item.query_selector("a").get_attribute("href")

        #         results.append({
        #             "title": title,
        #             "price": price,
        #             "shop": shop,
        #             "url": link
        #         })
        #     except Exception as e:
        #         continue  # Skip any items with missing data

        browser.close()
        return None

if __name__ == "__main__":
    keyword = "silver ring"
    data = scrape_etsy(keyword)
    for i, item in enumerate(data, start=1):
        print(f"{i}. {item['title']} | {item['price']} | {item['shop']} \n{item['url']}\n")
