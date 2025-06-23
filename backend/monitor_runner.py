#!/usr/bin/env python3
"""
Etsy Monitoring Runner
Executes monitoring rules and checks for changes using the multi-scraper system
"""

import uuid
from datetime import datetime
from monitoring_system import EtsyMonitor, MonitoringRule, ScrapedData

def run_monitoring_cycle():
    """Run a complete monitoring cycle for all active rules"""
    monitor = EtsyMonitor()
    
    # Get all active monitoring rules
    rules = monitor.get_monitoring_rules()
    
    if not rules:
        print("No active monitoring rules found.")
        return
    
    print(f"Running monitoring cycle for {len(rules)} rules...")
    
    for rule in rules:
        try:
            print(f"\nProcessing rule: {rule.rule_name} (ID: {rule.id})")
            print(f"  User: {rule.user_email}")
            print(f"  Scrapers: {[config['scraper_id'] for config in rule.scraper_configs]}")
            
            # Process the rule with multiple scrapers
            notifications = monitor.process_monitoring_rule(rule)
            
            if notifications:
                print(f"  Generated {len(notifications)} notifications:")
                for notification_type, message in notifications:
                    print(f"    [{notification_type}] {message}")
            else:
                print("  No changes detected")
                
        except Exception as e:
            print(f"  Error processing rule {rule.id}: {e}")
    
    print("\nMonitoring cycle completed!")

def create_example_monitoring_rule():
    """Create an example monitoring rule for testing"""
    monitor = EtsyMonitor()
    
    rule = MonitoringRule(
        id=f"rule_{uuid.uuid4().hex[:8]}",
        user_email="test@example.com",
        rule_name="Pearl Necklace Monitoring",
        scraper_configs=[
            {
                "scraper_id": "search",
                "params": {"keyword": "pearl necklace", "max_listings": 20},
                "priority": 1
            },
            {
                "scraper_id": "store",
                "params": {"store_url": "https://www.etsy.com/shop/PearlCraft", "max_listings": 10},
                "priority": 2
            }
        ],
        monitor_listing_count=True,
        monitor_sellers=["PearlCraft", "OceanGems", "PearlParadise"],
        monitor_price_changes=True,
        monitor_inventory_changes=True,
        monitor_description_changes=True,
        notification_threshold=5
    )
    
    monitor.add_monitoring_rule(rule)
    print(f"Created monitoring rule: {rule.id}")
    print(f"Rule name: {rule.rule_name}")
    print(f"User: {rule.user_email}")
    print(f"Scrapers: {[config['scraper_id'] for config in rule.scraper_configs]}")
    print(f"Monitoring sellers: {rule.monitor_sellers}")
    print(f"Listing count threshold: {rule.notification_threshold}")
    return rule.id

def create_search_only_rule():
    """Create a monitoring rule with only search scraper"""
    monitor = EtsyMonitor()
    
    rule = MonitoringRule(
        id=f"rule_{uuid.uuid4().hex[:8]}",
        user_email="test@example.com",
        rule_name="Silver Ring Search Monitoring",
        scraper_configs=[
            {
                "scraper_id": "search",
                "params": {"keyword": "silver ring", "max_listings": 15},
                "priority": 1
            }
        ],
        monitor_listing_count=True,
        monitor_sellers=["SilverSmith", "RingCraft"],
        monitor_price_changes=True,
        notification_threshold=3
    )
    
    monitor.add_monitoring_rule(rule)
    print(f"Created search-only monitoring rule: {rule.id}")
    print(f"Rule name: {rule.rule_name}")
    print(f"Keyword: silver ring")
    return rule.id

def show_pending_notifications():
    """Show all pending notifications"""
    monitor = EtsyMonitor()
    notifications = monitor.get_pending_notifications()
    
    if not notifications:
        print("No pending notifications.")
        return
    
    print(f"Found {len(notifications)} pending notifications:")
    for notification in notifications:
        print(f"\n[{notification['notification_type']}] {notification['message']}")
        print(f"  Rule: {notification['rule_name']}")
        print(f"  User: {notification['user_email']}")
        print(f"  Created: {notification['created_at']}")

def list_monitoring_rules():
    """List all monitoring rules"""
    monitor = EtsyMonitor()
    rules = monitor.get_monitoring_rules()
    
    if not rules:
        print("No monitoring rules found.")
        return
    
    print(f"Found {len(rules)} monitoring rules:")
    for rule in rules:
        print(f"\nRule ID: {rule.id}")
        print(f"  Name: {rule.rule_name}")
        print(f"  User: {rule.user_email}")
        print(f"  Scrapers: {[config['scraper_id'] for config in rule.scraper_configs]}")
        print(f"  Schedule: {rule.schedule_interval or 'Manual'}")
        print(f"  Monitor listing count: {rule.monitor_listing_count}")
        print(f"  Monitor sellers: {rule.monitor_sellers}")
        print(f"  Monitor price changes: {rule.monitor_price_changes}")
        print(f"  Monitor inventory changes: {rule.monitor_inventory_changes}")
        print(f"  Monitor description changes: {rule.monitor_description_changes}")
        print(f"  Threshold: {rule.notification_threshold}")
        print(f"  Created: {rule.created_at}")
        print(f"  Last checked: {rule.last_checked}")
        print(f"  Active: {rule.is_active}")

def list_available_scrapers():
    """List all available scrapers"""
    monitor = EtsyMonitor()
    scrapers = monitor.get_available_scrapers()
    
    if not scrapers:
        print("No scrapers available.")
        return
    
    print(f"Found {len(scrapers)} available scrapers:")
    for scraper in scrapers:
        print(f"\nScraper ID: {scraper['id']}")
        print(f"  Name: {scraper['name']}")
        print(f"  Description: {scraper['description']}")
        print(f"  Required params: {scraper['required_params']}")

def test_scraper(scraper_id: str, **params):
    """Test a specific scraper with given parameters"""
    monitor = EtsyMonitor()
    
    print(f"Testing scraper: {scraper_id}")
    print(f"Parameters: {params}")
    
    result = monitor.test_scraper(scraper_id, params)
    
    if result.get("success"):
        print("✅ Scraper test successful!")
        if scraper_id == "search":
            print(f"  Keyword: {result.get('keyword')}")
            print(f"  Total results: {result.get('total_results')}")
            print(f"  Listings scraped: {len(result.get('listings', []))}")
        elif scraper_id == "store":
            print(f"  Store: {result.get('store_name')}")
            print(f"  Total listings: {result.get('total_listings')}")
            print(f"  Store info: {result.get('store_info')}")
    else:
        print("❌ Scraper test failed!")
        print(f"  Error: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            run_monitoring_cycle()
        elif command == "create-example":
            create_example_monitoring_rule()
        elif command == "create-search-only":
            create_search_only_rule()
        elif command == "notifications":
            show_pending_notifications()
        elif command == "list-rules":
            list_monitoring_rules()
        elif command == "list-scrapers":
            list_available_scrapers()
        elif command == "test-search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else "pearl necklace"
            test_scraper("search", keyword=keyword)
        elif command == "test-store":
            store_url = sys.argv[2] if len(sys.argv) > 2 else "https://www.etsy.com/shop/PearlCraft"
            test_scraper("store", store_url=store_url)
        else:
            print("Unknown command. Available commands:")
            print("  run - Run monitoring cycle")
            print("  create-example - Create example monitoring rule (search + store)")
            print("  create-search-only - Create search-only monitoring rule")
            print("  notifications - Show pending notifications")
            print("  list-rules - List all monitoring rules")
            print("  list-scrapers - List available scrapers")
            print("  test-search <keyword> - Test search scraper")
            print("  test-store <url> - Test store scraper")
    else:
        print("Etsy Monitoring Runner (Multi-Scraper System)")
        print("Usage: python monitor_runner.py <command>")
        print("\nAvailable commands:")
        print("  run - Run monitoring cycle")
        print("  create-example - Create example monitoring rule (search + store)")
        print("  create-search-only - Create search-only monitoring rule")
        print("  notifications - Show pending notifications")
        print("  list-rules - List all monitoring rules")
        print("  list-scrapers - List available scrapers")
        print("  test-search <keyword> - Test search scraper")
        print("  test-store <url> - Test store scraper") 