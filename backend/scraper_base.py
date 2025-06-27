from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class BaseScraper(ABC):
    """Base class for all scrapers in the system"""
    
    def __init__(self, scraper_id: str, name: str):
        self.scraper_id = scraper_id
        self.name = name
    
    @abstractmethod
    async def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main scraping method - must be implemented by each scraper"""
        pass
    
    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters for this scraper"""
        pass
    
    def get_scraper_info(self) -> Dict[str, Any]:
        """Return metadata about this scraper"""
        return {
            "id": self.scraper_id,
            "name": self.name,
            "description": self.get_description(),
            "required_params": self.get_required_params()
        }
    
    @abstractmethod
    def get_description(self) -> str:
        """Return description of what this scraper does"""
        pass
    
    @abstractmethod
    def get_required_params(self) -> list:
        """Return list of required parameters for this scraper"""
        pass
    
    def pre_scrape_hook(self, params: Dict[str, Any]) -> None:
        """Optional hook called before scraping starts"""
        pass
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Optional hook called after scraping completes"""
        pass
    
    def handle_error(self, error: Exception, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors during scraping"""
        return {
            "scraper_id": self.scraper_id,
            "error": str(error),
            "params": params,
            "scraped_at": datetime.now().isoformat(),
            "success": False
        } 