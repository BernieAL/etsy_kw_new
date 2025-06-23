#!/usr/bin/env python3
"""
Production Worker for Etsy Monitoring System
Runs continuously and executes monitoring rules on schedule
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import signal
import sys

from monitoring_system import EtsyMonitor, MonitoringRule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringWorker:
    """Background worker for executing monitoring rules"""
    
    def __init__(self, check_interval: int = 60):
        self.monitor = EtsyMonitor()
        self.check_interval = check_interval  # seconds
        self.running = True
        self.intervals = {
            '30min': timedelta(minutes=30),
            '5hr': timedelta(hours=5),
            '12hr': timedelta(hours=12),
            '24hr': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'biweekly': timedelta(weeks=2)
        }
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def is_rule_due(self, rule: MonitoringRule) -> bool:
        """Check if a rule is due for execution"""
        if not rule.schedule_interval or not rule.last_checked:
            return False
        
        if rule.schedule_interval not in self.intervals:
            logger.warning(f"Unknown interval: {rule.schedule_interval}")
            return False
        
        last_checked = datetime.fromisoformat(rule.last_checked)
        interval = self.intervals[rule.schedule_interval]
        next_run = last_checked + interval
        
        return datetime.now() >= next_run
    
    def get_due_rules(self) -> List[MonitoringRule]:
        """Get all rules that are due for execution"""
        all_rules = self.monitor.get_monitoring_rules()
        due_rules = []
        
        for rule in all_rules:
            if self.is_rule_due(rule):
                due_rules.append(rule)
        
        return due_rules
    
    def execute_rule(self, rule: MonitoringRule) -> bool:
        """Execute a single monitoring rule"""
        try:
            logger.info(f"Executing rule: {rule.rule_name} (ID: {rule.id})")
            logger.info(f"  User: {rule.user_email}")
            logger.info(f"  Scrapers: {[config['scraper_id'] for config in rule.scraper_configs]}")
            
            # Process the rule
            notifications = self.monitor.process_monitoring_rule(rule)
            
            if notifications:
                logger.info(f"  Generated {len(notifications)} notifications:")
                for notification_type, message in notifications:
                    logger.info(f"    [{notification_type}] {message}")
            else:
                logger.info("  No changes detected")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.id}: {e}")
            return False
    
    def run_cycle(self):
        """Run one monitoring cycle"""
        try:
            due_rules = self.get_due_rules()
            
            if not due_rules:
                logger.debug("No rules due for execution")
                return
            
            logger.info(f"Found {len(due_rules)} rules due for execution")
            
            for rule in due_rules:
                success = self.execute_rule(rule)
                if success:
                    logger.info(f"Successfully executed rule: {rule.rule_name}")
                else:
                    logger.error(f"Failed to execute rule: {rule.rule_name}")
                
                # Small delay between rules to be respectful
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def run_forever(self):
        """Run the worker continuously"""
        logger.info("Starting monitoring worker...")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        while self.running:
            try:
                self.run_cycle()
                
                # Wait for next check
                if self.running:
                    time.sleep(self.check_interval)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("Monitoring worker stopped")

def main():
    """Main entry point for the worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Etsy Monitoring Worker')
    parser.add_argument('--check-interval', type=int, default=60,
                       help='Interval between checks in seconds (default: 60)')
    parser.add_argument('--run-once', action='store_true',
                       help='Run one cycle and exit')
    
    args = parser.parse_args()
    
    worker = MonitoringWorker(check_interval=args.check_interval)
    
    if args.run_once:
        logger.info("Running single monitoring cycle...")
        worker.run_cycle()
        logger.info("Single cycle completed")
    else:
        worker.run_forever()

if __name__ == "__main__":
    main() 