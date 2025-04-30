"""
File operations utilities for the Etsy Keyword Analyzer.
Handles report file creation, directory management, and data formatting.
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from .logger import get_logger

logger = get_logger("file_operations")

class ReportPathBuilder:
    """
    Utility class for managing report file paths and operations.
    Handles creation of directories and files for reports.
    
    Directory structure:
        report_root/
            user_id/
                date/
                    report_{job_id}_{timestamp}.csv
    """
    
    def __init__(self, root_dir: str):
        """
        Initialize the ReportPathBuilder with the root directory for reports.
        
        Args:
            root_dir (str): Root directory where all reports will be stored
        """
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        
        self.user_id_dir: Optional[Path] = None
        self.date_dir: Optional[Path] = None
        self.curr_output_filepath: Optional[Path] = None
        
        self.user_id: Optional[str] = None
        self.job_id: Optional[str] = None
        self.date: Optional[str] = None
    
    def make_user_subdir(self, user_id: str) -> Path:
        """
        Create a subdirectory for a specific user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Path: Path to the created user directory
        """
        self.user_id = str(user_id)
        self.user_id_dir = self.root / self.user_id
        self.user_id_dir.mkdir(exist_ok=True)
        logger.info(f"Created user directory: {self.user_id_dir}")
        return self.user_id_dir
    
    def make_date_subdir(self, date: str) -> Path:
        """
        Create a subdirectory for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            Path: Path to the created date directory
            
        Raises:
            ValueError: If user subdirectory hasn't been created yet
        """
        if self.user_id_dir is None:
            raise ValueError("User subdirectory must be created before date subdirectory")
        
        self.date = date
        self.date_dir = self.user_id_dir / date
        self.date_dir.mkdir(exist_ok=True)
        logger.info(f"Created date directory: {self.date_dir}")
        return self.date_dir
    
    def make_report_file(self, job_id: str) -> Path:
        """
        Create a report file for a specific job.
        
        Args:
            job_id (str): Job identifier
            
        Returns:
            Path: Path to the created report file
            
        Raises:
            ValueError: If user or date subdirectories haven't been created yet
        """
        if self.user_id_dir is None or self.date_dir is None:
            raise ValueError("User and date subdirectories must be created before report file")
        
        self.job_id = job_id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{self.job_id}_{timestamp}.csv"
        self.curr_output_filepath = self.date_dir / filename
        
        # Create empty file
        self.curr_output_filepath.touch()
        logger.info(f"Created report file: {self.curr_output_filepath}")
        return self.curr_output_filepath
    
    def write_file_formatted(self, data: List[Dict[str, Any]]) -> None:
        """
        Write data to a CSV file in a formatted structure.
        
        Args:
            data (List[Dict[str, Any]]): List of dictionaries containing URL data
                Each dict should have: url, tags, search_terms
        
        Raises:
            ValueError: If no output filepath has been set
        """
        if self.curr_output_filepath is None:
            raise ValueError("No output filepath set. Call make_report_file first.")
        
        with open(self.curr_output_filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['URL', 'Tags', 'Related Search Terms'])
            
            # Write data rows
            for item in data:
                url = item.get('url', '')
                tags = '; '.join(item.get('tags', []))
                search_terms = '; '.join(item.get('search_terms', []))
                writer.writerow([url, tags, search_terms])
        
        logger.info(f"Wrote data to report file: {self.curr_output_filepath}") 