import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os

from scraper_orchestrator import ScraperOrchestrator
from scrapers.etsy_search_scraper import EtsySearchScraper
from scrapers.etsy_store_scraper import EtsyStoreScraper

@dataclass
class MonitoringRule:
    id: str
    user_email: str
    rule_name: str
    scraper_configs: List[Dict[str, Any]]  # List of scraper configurations
    schedule_interval: Optional[str] = None
    monitor_listing_count: bool = False
    monitor_sellers: List[str] = None
    monitor_price_changes: bool = False
    monitor_inventory_changes: bool = False
    monitor_description_changes: bool = False
    notification_threshold: int = 0
    created_at: str = None
    last_checked: str = None
    is_active: bool = True

@dataclass
class ScrapedData:
    rule_id: str
    scraper_results: List[Dict[str, Any]]  # Results from multiple scrapers
    scraped_at: str

class EtsyMonitor:
    def __init__(self, db_path: str = None):
        # Use environment variable or default to local file
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'etsy_monitor.db')
        self.orchestrator = ScraperOrchestrator()
        self.init_database()
        self._register_default_scrapers()
    
    def _register_default_scrapers(self):
        """Register all available scrapers with the orchestrator"""
        self.orchestrator.register_default_scrapers()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Monitoring rules table (updated for multi-scraper support)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_rules (
                id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                scraper_configs TEXT,  -- JSON array of scraper configurations
                schedule_interval TEXT,
                monitor_listing_count BOOLEAN DEFAULT FALSE,
                monitor_sellers TEXT,  -- JSON array of seller names
                monitor_price_changes BOOLEAN DEFAULT FALSE,
                monitor_inventory_changes BOOLEAN DEFAULT FALSE,
                monitor_description_changes BOOLEAN DEFAULT FALSE,
                notification_threshold INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_checked TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Historical data table (updated for multi-scraper results)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                scraper_results TEXT,  -- JSON array of scraper results
                scraped_at TEXT NOT NULL,
                FOREIGN KEY (rule_id) REFERENCES monitoring_rules (id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_sent BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (rule_id) REFERENCES monitoring_rules (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_monitoring_rule(self, rule: MonitoringRule) -> str:
        """Add a new monitoring rule"""
        if not rule.created_at:
            rule.created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitoring_rules 
            (id, user_email, rule_name, scraper_configs, schedule_interval,
             monitor_listing_count, monitor_sellers, monitor_price_changes,
             monitor_inventory_changes, monitor_description_changes,
             notification_threshold, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.id, rule.user_email, rule.rule_name,
            json.dumps(rule.scraper_configs), rule.schedule_interval,
            rule.monitor_listing_count, json.dumps(rule.monitor_sellers or []),
            rule.monitor_price_changes, rule.monitor_inventory_changes,
            rule.monitor_description_changes, rule.notification_threshold,
            rule.created_at, rule.is_active
        ))
        
        conn.commit()
        conn.close()
        return rule.id
    
    def get_monitoring_rules(self, user_email: str = None) -> List[MonitoringRule]:
        """Get all monitoring rules, optionally filtered by user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_email:
            cursor.execute('SELECT * FROM monitoring_rules WHERE user_email = ? AND is_active = TRUE', (user_email,))
        else:
            cursor.execute('SELECT * FROM monitoring_rules WHERE is_active = TRUE')
        
        rules = []
        for row in cursor.fetchall():
            rule = MonitoringRule(
                id=row[0], user_email=row[1], rule_name=row[2],
                scraper_configs=json.loads(row[3]) if row[3] else [],
                schedule_interval=row[4], monitor_listing_count=bool(row[5]),
                monitor_sellers=json.loads(row[6]) if row[6] else [],
                monitor_price_changes=bool(row[7]), monitor_inventory_changes=bool(row[8]),
                monitor_description_changes=bool(row[9]), notification_threshold=row[10],
                created_at=row[11], last_checked=row[12], is_active=bool(row[13])
            )
            rules.append(rule)
        
        conn.close()
        return rules
    
    def save_scraped_data(self, rule_id: str, data: ScrapedData):
        """Save scraped data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO historical_data 
            (rule_id, scraper_results, scraped_at)
            VALUES (?, ?, ?)
        ''', (
            rule_id, json.dumps(data.scraper_results), data.scraped_at
        ))
        
        # Update last_checked timestamp
        cursor.execute('''
            UPDATE monitoring_rules 
            SET last_checked = ? 
            WHERE id = ?
        ''', (data.scraped_at, rule_id))
        
        conn.commit()
        conn.close()
    
    def get_previous_data(self, rule_id: str) -> Optional[ScrapedData]:
        """Get the most recent scraped data for a rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT scraper_results, scraped_at
            FROM historical_data 
            WHERE rule_id = ? 
            ORDER BY scraped_at DESC 
            LIMIT 1
        ''', (rule_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ScrapedData(
                rule_id=rule_id,
                scraper_results=json.loads(row[0]),
                scraped_at=row[1]
            )
        return None
    
    def check_listing_count_change(self, rule: MonitoringRule, current_data: ScrapedData) -> Optional[str]:
        """Check if listing count has changed significantly"""
        if not rule.monitor_listing_count:
            return None
        
        previous_data = self.get_previous_data(rule.id)
        if not previous_data:
            return None
        
        # Find search scraper results in both current and previous data
        current_search_results = None
        previous_search_results = None
        
        for result in current_data.scraper_results:
            if result.get("scraper_id") == "search":
                current_search_results = result
                break
        
        for result in previous_data.scraper_results:
            if result.get("scraper_id") == "search":
                previous_search_results = result
                break
        
        if not current_search_results or not previous_search_results:
            return None
        
        current_count = current_search_results.get("total_results", 0)
        previous_count = previous_search_results.get("total_results", 0)
        
        change = current_count - previous_count
        threshold = rule.notification_threshold
        
        if abs(change) >= threshold:
            direction = "increased" if change > 0 else "decreased"
            return f"Listing count for search results {direction} by {abs(change)} (from {previous_count} to {current_count})"
        
        return None
    
    def check_seller_changes(self, rule: MonitoringRule, current_data: ScrapedData) -> List[str]:
        """Check for changes in monitored sellers"""
        if not rule.monitor_sellers:
            return []
        
        previous_data = self.get_previous_data(rule.id)
        if not previous_data:
            return []
        
        notifications = []
        monitored_sellers = set(rule.monitor_sellers)
        
        # Process search scraper results
        current_search_results = None
        previous_search_results = None
        
        for result in current_data.scraper_results:
            if result.get("scraper_id") == "search":
                current_search_results = result
                break
        
        for result in previous_data.scraper_results:
            if result.get("scraper_id") == "search":
                previous_search_results = result
                break
        
        if current_search_results and previous_search_results:
            current_listings = {listing['shop']: listing for listing in current_search_results.get("listings", [])}
            previous_listings = {listing['shop']: listing for listing in previous_search_results.get("listings", [])}
            
            for seller in monitored_sellers:
                current_listing = current_listings.get(seller)
                previous_listing = previous_listings.get(seller)
                
                if not current_listing and previous_listing:
                    notifications.append(f"Seller '{seller}' no longer appears in search results")
                
                elif current_listing and previous_listing:
                    # Check price changes
                    if rule.monitor_price_changes and current_listing['price'] != previous_listing['price']:
                        notifications.append(f"Price change for '{seller}': {previous_listing['price']} → {current_listing['price']}")
                    
                    # Check title/description changes
                    if rule.monitor_description_changes and current_listing['title'] != previous_listing['title']:
                        notifications.append(f"Title change for '{seller}': '{previous_listing['title']}' → '{current_listing['title']}'")
                
                elif current_listing and not previous_listing:
                    notifications.append(f"New listing from '{seller}': {current_listing['title']} - {current_listing['price']}")
        
        return notifications
    
    def create_notification(self, rule_id: str, notification_type: str, message: str):
        """Create a notification record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications 
            (rule_id, notification_type, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (rule_id, notification_type, message, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    async def process_monitoring_rule(self, rule: MonitoringRule) -> List[tuple]:
        """Process a monitoring rule with multiple scrapers"""
        notifications = []
        
        # Clear any existing jobs
        self.orchestrator.clear_queue()
        
        # Add jobs for each scraper configuration
        for config in rule.scraper_configs:
            self.orchestrator.add_scraping_job(
                scraper_id=config["scraper_id"],
                params=config["params"],
                priority=config.get("priority", 1)
            )
        
        # Execute all scrapers sequentially (now async)
        results = await self.orchestrator.execute_jobs()
        
        # Create ScrapedData object
        scraped_data = ScrapedData(
            rule_id=rule.id,
            scraper_results=results,
            scraped_at=datetime.now().isoformat()
        )
        
        # Check for changes and generate notifications
        if rule.monitor_listing_count:
            count_notification = self.check_listing_count_change(rule, scraped_data)
            if count_notification:
                notifications.append(("listing_count", count_notification))
        
        if rule.monitor_sellers:
            seller_notifications = self.check_seller_changes(rule, scraped_data)
            for notification in seller_notifications:
                notifications.append(("seller_change", notification))
        
        # Save current data
        self.save_scraped_data(rule.id, scraped_data)
        
        # Create notification records
        for notification_type, message in notifications:
            self.create_notification(rule.id, notification_type, message)
        
        return notifications
    
    def get_pending_notifications(self, user_email: str = None) -> List[Dict]:
        """Get all pending notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_email:
            cursor.execute('''
                SELECT n.*, r.rule_name, r.user_email
                FROM notifications n
                JOIN monitoring_rules r ON n.rule_id = r.id
                WHERE r.user_email = ? AND n.is_sent = FALSE
                ORDER BY n.created_at DESC
            ''', (user_email,))
        else:
            cursor.execute('''
                SELECT n.*, r.rule_name, r.user_email
                FROM notifications n
                JOIN monitoring_rules r ON n.rule_id = r.id
                WHERE n.is_sent = FALSE
                ORDER BY n.created_at DESC
            ''')
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "rule_id": row[1],
                "notification_type": row[2],
                "message": row[3],
                "created_at": row[4],
                "rule_name": row[6],
                "user_email": row[7]
            })
        
        conn.close()
        return notifications
    
    def get_available_scrapers(self) -> List[Dict[str, Any]]:
        """Get list of all available scrapers"""
        return self.orchestrator.get_available_scrapers()
    
    async def test_scraper(self, scraper_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific scraper with given parameters"""
        return await self.orchestrator.test_scraper(scraper_id, params)

# Example usage
if __name__ == "__main__":
    monitor = EtsyMonitor()
    
    # Example: Create a monitoring rule with multiple scrapers
    rule = MonitoringRule(
        id="rule_001",
        user_email="test@example.com",
        rule_name="Pearl Necklace Monitoring",
        scraper_configs=[
            {
                "scraper_id": "search",
                "params": {"keyword": "pearl necklace"},
                "priority": 1
            },
            {
                "scraper_id": "store",
                "params": {"store_url": "https://www.etsy.com/shop/PearlCraft"},
                "priority": 2
            }
        ],
        monitor_listing_count=True,
        monitor_sellers=["PearlCraft", "OceanGems"],
        monitor_price_changes=True,
        notification_threshold=5
    )
    
    monitor.add_monitoring_rule(rule)
    print("Monitoring rule created successfully!") 