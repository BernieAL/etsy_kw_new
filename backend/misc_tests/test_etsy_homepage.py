import asyncio
from scrapers.etsy_search_scraper import EtsySearchScraper

async def main():
    scraper = EtsySearchScraper()
    result = await scraper.test_etsy_homepage()
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 