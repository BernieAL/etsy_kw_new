from typing import List, Dict, Any, Optional
from scraper_base import BaseScraper
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperOrchestrator:
    """Orchestrates multiple scrapers and executes them sequentially"""
    
    def __init__(self, delay_between_scrapers: int = 2):
        self.scrapers: Dict[str, BaseScraper] = {}
        self.scraper_queue: List[Dict[str, Any]] = []
        self.delay_between_scrapers = delay_between_scrapers
        self.execution_history: List[Dict[str, Any]] = []
    
    def register_scraper(self, scraper: BaseScraper) -> None:
        """Register a scraper with the orchestrator"""
        if scraper.scraper_id in self.scrapers:
            logger.warning(f"Scraper {scraper.scraper_id} already registered, overwriting")
        
        self.scrapers[scraper.scraper_id] = scraper
        logger.info(f"Registered scraper: {scraper.name} (ID: {scraper.scraper_id})")
    
    def add_scraping_job(self, scraper_id: str, params: Dict[str, Any], priority: int = 1, job_id: Optional[str] = None) -> str:
        """Add a scraping job to the queue"""
        if scraper_id not in self.scrapers:
            raise ValueError(f"Scraper {scraper_id} not found. Available scrapers: {list(self.scrapers.keys())}")
        
        if not job_id:
            job_id = f"job_{int(time.time())}_{len(self.scraper_queue)}"
        
        job = {
            "job_id": job_id,
            "scraper_id": scraper_id,
            "params": params,
            "priority": priority,
            "created_at": time.time(),
            "status": "queued"
        }
        
        self.scraper_queue.append(job)
        logger.info(f"Added job {job_id} for scraper {scraper_id} with priority {priority}")
        return job_id
    
    def clear_queue(self) -> None:
        """Clear all jobs from the queue"""
        self.scraper_queue.clear()
        logger.info("Cleared scraper queue")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current status of the queue"""
        return {
            "queue_length": len(self.scraper_queue),
            "jobs": self.scraper_queue.copy(),
            "available_scrapers": list(self.scrapers.keys())
        }
    
    def execute_jobs(self, clear_queue: bool = True) -> List[Dict[str, Any]]:
        """Execute all jobs in the queue sequentially"""
        if not self.scraper_queue:
            logger.info("No jobs in queue to execute")
            return []
        
        results = []
        execution_start = datetime.now()
        
        logger.info(f"Starting execution of {len(self.scraper_queue)} jobs")
        
        # Sort by priority (higher priority first)
        self.scraper_queue.sort(key=lambda x: x["priority"], reverse=True)
        
        for i, job in enumerate(self.scraper_queue):
            job_start = datetime.now()
            job["status"] = "running"
            
            try:
                scraper = self.scrapers[job["scraper_id"]]
                logger.info(f"Executing job {job['job_id']}: {scraper.name}")
                
                # Validate parameters
                if not scraper.validate_params(job["params"]):
                    error_msg = f"Invalid parameters for scraper {job['scraper_id']}"
                    logger.error(error_msg)
                    result = {
                        "job_id": job["job_id"],
                        "scraper_id": job["scraper_id"],
                        "error": error_msg,
                        "params": job["params"],
                        "scraped_at": datetime.now().isoformat(),
                        "success": False,
                        "execution_time": 0
                    }
                    results.append(result)
                    job["status"] = "failed"
                    continue
                
                # Pre-scrape hook
                scraper.pre_scrape_hook(job["params"])
                
                # Execute scraping
                result = scraper.scrape(job["params"])
                
                # Post-scrape hook
                scraper.post_scrape_hook(result)
                
                # Add metadata
                result["job_id"] = job["job_id"]
                result["scraper_id"] = job["scraper_id"]
                result["success"] = True
                result["execution_time"] = (datetime.now() - job_start).total_seconds()
                
                results.append(result)
                job["status"] = "completed"
                
                logger.info(f"Completed job {job['job_id']} in {result['execution_time']:.2f}s")
                
            except Exception as e:
                logger.error(f"Error executing job {job['job_id']}: {e}")
                result = scraper.handle_error(e, job["params"])
                result["job_id"] = job["job_id"]
                result["execution_time"] = (datetime.now() - job_start).total_seconds()
                results.append(result)
                job["status"] = "failed"
            
            # Add delay between scrapers (except for the last one)
            if i < len(self.scraper_queue) - 1:
                logger.info(f"Waiting {self.delay_between_scrapers}s before next scraper...")
                time.sleep(self.delay_between_scrapers)
        
        # Record execution history
        execution_record = {
            "execution_id": f"exec_{int(time.time())}",
            "start_time": execution_start.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_jobs": len(self.scraper_queue),
            "successful_jobs": len([r for r in results if r.get("success", False)]),
            "failed_jobs": len([r for r in results if not r.get("success", False)]),
            "results": results
        }
        self.execution_history.append(execution_record)
        
        # Clear queue if requested
        if clear_queue:
            self.clear_queue()
        
        total_time = (datetime.now() - execution_start).total_seconds()
        logger.info(f"Completed execution of {len(results)} jobs in {total_time:.2f}s")
        
        return results
    
    def get_available_scrapers(self) -> List[Dict[str, Any]]:
        """Get list of all available scrapers with their metadata"""
        return [scraper.get_scraper_info() for scraper in self.scrapers.values()]
    
    def get_scraper(self, scraper_id: str) -> Optional[BaseScraper]:
        """Get a specific scraper by ID"""
        return self.scrapers.get(scraper_id)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def test_scraper(self, scraper_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific scraper with given parameters"""
        if scraper_id not in self.scrapers:
            return {"error": f"Scraper {scraper_id} not found"}
        
        scraper = self.scrapers[scraper_id]
        
        try:
            if not scraper.validate_params(params):
                return {"error": "Invalid parameters"}
            
            result = scraper.scrape(params)
            result["success"] = True
            return result
            
        except Exception as e:
            return scraper.handle_error(e, params) 