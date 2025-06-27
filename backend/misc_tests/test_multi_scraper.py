#!/usr/bin/env python3
"""
Test script for the multi-scraper monitoring system
"""

from monitoring_system import EtsyMonitor, MonitoringRule
from scraper_orchestrator import ScraperOrchestrator
from scrapers.etsy_search_scraper import EtsySearchScraper
from scrapers.etsy_store_scraper import EtsyStoreScraper
import uuid

def test_scraper_orchestrator():
    """Test the scraper orchestrator directly"""
    print("=== Testing Scraper Orchestrator ===")
    
    orchestrator = ScraperOrchestrator()
    
    # Register scrapers
    orchestrator.register_scraper(EtsySearchScraper())
    orchestrator.register_scraper(EtsyStoreScraper())
    
    print(f"Registered scrapers: {[s.scraper_id for s in orchestrator.scrapers.values()]}")
    
    # Test individual scrapers
    print("\n--- Testing Search Scraper ---")
    search_result = orchestrator.test_scraper("search", {"keyword": "silver ring"})
    print(f"Search result success: {search_result.get('success')}")
    if search_result.get('success'):
        print(f"  Total results: {search_result.get('total_results')}")
        print(f"  Listings: {len(search_result.get('listings', []))}")
    
    print("\n--- Testing Store Scraper ---")
    store_result = orchestrator.test_scraper("store", {"store_url": "https://www.etsy.com/shop/PearlCraft"})
    print(f"Store result success: {store_result.get('success')}")
    if store_result.get('success'):
        print(f"  Store name: {store_result.get('store_name')}")
        print(f"  Total listings: {store_result.get('total_listings')}")
    
    # Test sequential execution
    print("\n--- Testing Sequential Execution ---")
    orchestrator.add_scraping_job("search", {"keyword": "pearl necklace"}, priority=1)
    orchestrator.add_scraping_job("store", {"store_url": "https://www.etsy.com/shop/PearlCraft"}, priority=2)
    
    results = orchestrator.execute_jobs()
    print(f"Executed {len(results)} jobs")
    for result in results:
        print(f"  {result['scraper_id']}: {'✅' if result.get('success') else '❌'}")

def test_monitoring_system():
    """Test the monitoring system with multi-scraper support"""
    print("\n=== Testing Monitoring System ===")
    
    monitor = EtsyMonitor()
    
    # Create a test rule
    rule = MonitoringRule(
        id=f"test_rule_{uuid.uuid4().hex[:8]}",
        user_email="test@example.com",
        rule_name="Test Multi-Scraper Rule",
        scraper_configs=[
            {
                "scraper_id": "search",
                "params": {"keyword": "silver ring", "max_listings": 5},
                "priority": 1
            },
            {
                "scraper_id": "store",
                "params": {"store_url": "https://www.etsy.com/shop/PearlCraft", "max_listings": 3},
                "priority": 2
            }
        ],
        monitor_listing_count=True,
        monitor_sellers=["PearlCraft"],
        monitor_price_changes=True,
        notification_threshold=1
    )
    
    # Add the rule
    monitor.add_monitoring_rule(rule)
    print(f"Created test rule: {rule.id}")
    
    # Process the rule
    print("\n--- Processing Rule ---")
    notifications = monitor.process_monitoring_rule(rule)
    print(f"Generated {len(notifications)} notifications")
    
    # Check notifications
    print("\n--- Checking Notifications ---")
    all_notifications = monitor.get_pending_notifications()
    print(f"Total pending notifications: {len(all_notifications)}")
    
    # List rules
    print("\n--- Listing Rules ---")
    rules = monitor.get_monitoring_rules()
    print(f"Total rules: {len(rules)}")
    for r in rules:
        print(f"  {r.rule_name} ({r.id}) - {len(r.scraper_configs)} scrapers")

def test_available_scrapers():
    """Test listing available scrapers"""
    print("\n=== Testing Available Scrapers ===")
    
    monitor = EtsyMonitor()
    scrapers = monitor.get_available_scrapers()
    
    print(f"Available scrapers: {len(scrapers)}")
    for scraper in scrapers:
        print(f"\n{scraper['name']} ({scraper['id']})")
        print(f"  Description: {scraper['description']}")
        print(f"  Required params: {scraper['required_params']}")

if __name__ == "__main__":
    print("🧪 Testing Multi-Scraper Monitoring System")
    print("=" * 50)
    
    try:
        test_scraper_orchestrator()
        test_monitoring_system()
        test_available_scrapers()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 