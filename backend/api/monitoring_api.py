from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os

from monitoring_system import EtsyMonitor, MonitoringRule
from monitor_runner import run_monitoring_cycle

# Load configuration from environment variables
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

app = FastAPI(title="Etsy Monitoring API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_keywords_from_configs(scraper_configs: List[dict]) -> str:
    """Extract keywords from scraper configurations"""
    keywords = []
    for config in scraper_configs:
        if "params" in config and "keyword" in config["params"]:
            keywords.append(config["params"]["keyword"])
    return ", ".join(keywords) if keywords else "No keywords"



# Pydantic models for API requests/responses
class MonitoringRuleCreate(BaseModel):
    rule_name: str
    user_email: str
    scraper_configs: List[dict]  # List of scraper configurations
    schedule_interval: Optional[str] = None
    monitor_listing_count: bool = False
    monitor_sellers: List[str] = []
    monitor_price_changes: bool = False
    monitor_inventory_changes: bool = False
    monitor_description_changes: bool = False
    notification_threshold: int = 0

class MonitoringRuleResponse(BaseModel):
    id: str
    rule_name: str
    keyword: str
    user_email: str
    monitor_listing_count: bool
    monitor_sellers: List[str]
    monitor_price_changes: bool
    monitor_inventory_changes: bool
    monitor_description_changes: bool
    notification_threshold: int
    created_at: str
    last_checked: Optional[str]
    is_active: bool

class NotificationResponse(BaseModel):
    id: int
    rule_id: str
    notification_type: str
    message: str
    created_at: str
    keyword: str
    user_email: str

@app.post("/monitoring-rules", response_model=MonitoringRuleResponse)
async def create_monitoring_rule(rule_data: MonitoringRuleCreate):
    """Create a new monitoring rule"""
    monitor = EtsyMonitor()
    
    rule = MonitoringRule(
        id=f"rule_{uuid.uuid4().hex[:8]}",
        user_email=rule_data.user_email,
        rule_name=rule_data.rule_name,
        scraper_configs=rule_data.scraper_configs,
        schedule_interval=rule_data.schedule_interval,
        monitor_listing_count=rule_data.monitor_listing_count,
        monitor_sellers=rule_data.monitor_sellers,
        monitor_price_changes=rule_data.monitor_price_changes,
        monitor_inventory_changes=rule_data.monitor_inventory_changes,
        monitor_description_changes=rule_data.monitor_description_changes,
        notification_threshold=rule_data.notification_threshold
    )
    
    monitor.add_monitoring_rule(rule)
    
    return MonitoringRuleResponse(
        id=rule.id,
        rule_name=rule.rule_name,
        keyword=extract_keywords_from_configs(rule.scraper_configs),
        user_email=rule.user_email,
        monitor_listing_count=rule.monitor_listing_count,
        monitor_sellers=rule.monitor_sellers,
        monitor_price_changes=rule.monitor_price_changes,
        monitor_inventory_changes=rule.monitor_inventory_changes,
        monitor_description_changes=rule.monitor_description_changes,
        notification_threshold=rule.notification_threshold,
        created_at=rule.created_at,
        last_checked=rule.last_checked,
        is_active=rule.is_active
    )

@app.get("/monitoring-rules", response_model=List[MonitoringRuleResponse])
async def list_monitoring_rules(user_email: Optional[str] = None):
    """List all monitoring rules, optionally filtered by user"""
    monitor = EtsyMonitor()
    rules = monitor.get_monitoring_rules(user_email)
    
    return [
        MonitoringRuleResponse(
            id=rule.id,
            rule_name=rule.rule_name,
            keyword=extract_keywords_from_configs(rule.scraper_configs),
            user_email=rule.user_email,
            monitor_listing_count=rule.monitor_listing_count,
            monitor_sellers=rule.monitor_sellers,
            monitor_price_changes=rule.monitor_price_changes,
            monitor_inventory_changes=rule.monitor_inventory_changes,
            monitor_description_changes=rule.monitor_description_changes,
            notification_threshold=rule.notification_threshold,
            created_at=rule.created_at,
            last_checked=rule.last_checked,
            is_active=rule.is_active
        )
        for rule in rules
    ]

@app.get("/monitoring-rules/{rule_id}", response_model=MonitoringRuleResponse)
async def get_monitoring_rule(rule_id: str):
    """Get a specific monitoring rule"""
    monitor = EtsyMonitor()
    rules = monitor.get_monitoring_rules()
    
    for rule in rules:
        if rule.id == rule_id:
            return MonitoringRuleResponse(
                id=rule.id,
                rule_name=rule.rule_name,
                keyword=extract_keywords_from_configs(rule.scraper_configs),
                user_email=rule.user_email,
                monitor_listing_count=rule.monitor_listing_count,
                monitor_sellers=rule.monitor_sellers,
                monitor_price_changes=rule.monitor_price_changes,
                monitor_inventory_changes=rule.monitor_inventory_changes,
                monitor_description_changes=rule.monitor_description_changes,
                notification_threshold=rule.notification_threshold,
                created_at=rule.created_at,
                last_checked=rule.last_checked,
                is_active=rule.is_active
            )
    
    raise HTTPException(status_code=404, detail="Monitoring rule not found")

@app.delete("/monitoring-rules/{rule_id}")
async def delete_monitoring_rule(rule_id: str):
    """Delete a monitoring rule (deactivate it)"""
    monitor = EtsyMonitor()
    
    # For now, we'll just mark it as inactive
    # In a real implementation, you'd want to add a method to the EtsyMonitor class
    conn = monitor.db_path
    import sqlite3
    conn = sqlite3.connect(conn)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE monitoring_rules 
        SET is_active = FALSE 
        WHERE id = ?
    ''', (rule_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Monitoring rule not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Monitoring rule deactivated successfully"}

@app.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(user_email: Optional[str] = None):
    """Get all pending notifications"""
    monitor = EtsyMonitor()
    notifications = monitor.get_pending_notifications(user_email)
    
    return [
        NotificationResponse(
            id=notification['id'],
            rule_id=notification['rule_id'],
            notification_type=notification['notification_type'],
            message=notification['message'],
            created_at=notification['created_at'],
            keyword=notification.get('rule_name', 'Unknown'),  # Use rule_name as keyword
            user_email=notification['user_email']
        )
        for notification in notifications
    ]

@app.post("/monitoring/run")
async def run_monitoring():
    """Run a monitoring cycle for all active rules"""
    try:
        run_monitoring_cycle()
        return {"message": "Monitoring cycle completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring cycle failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/test-scrape")
async def test_scrape(request: dict):
    """Test scraping with custom parameters"""
    try:
        monitor = EtsyMonitor()
        
        # Extract parameters from request
        scraper_id = request.get("scraper_id", "search")
        params = request.get("params", {})
        
        # Test the scraper (now async)
        result = await monitor.test_scraper(scraper_id, params)
        
        return {
            "success": True,
            "result": result,
            "message": f"Test scrape completed for {scraper_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test scrape failed: {str(e)}")

@app.get("/scrapers")
async def get_scrapers():
    """Get list of available scrapers"""
    try:
        monitor = EtsyMonitor()
        scrapers = monitor.get_available_scrapers()
        return scrapers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scrapers: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT) 